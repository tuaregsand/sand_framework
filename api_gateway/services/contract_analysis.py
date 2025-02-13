"""
Contract analysis service.
"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from api_gateway.models.database import Contract, Analysis, Project
from api_gateway.models.schemas import AnalysisStatus
from api_gateway.tasks.contract_analysis import analyze_contract
from api_gateway.core.queue import get_task_info
from api_gateway.core.monitoring import track_analysis
from api_gateway.core.validation import validate_contract, ContractValidationError

logger = logging.getLogger(__name__)

@track_analysis
async def start_contract_analysis(
    db: AsyncSession,
    source_code: str,
    project_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Start contract analysis.
    
    Args:
        db: Database session
        source_code: Contract source code
        project_id: Optional project ID
        
    Returns:
        Dict containing:
        - analysis_id: ID of the created analysis
        - task_id: ID of the Celery task
        - status: Analysis status
    """
    try:
        # Validate contract
        try:
            await validate_contract(source_code)
        except ContractValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Create contract in database if project_id is provided
        contract = None
        if project_id:
            # Verify project exists
            project = await db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = project.scalar_one_or_none()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {project_id} not found"
                )
            
            # Create contract
            contract = Contract(
                source_code=source_code,
                project_id=project_id
            )
            db.add(contract)
            await db.commit()
            await db.refresh(contract)
        
        # Create analysis record
        analysis = Analysis(
            contract_id=contract.id if contract else None,
            project_id=project_id,
            status=AnalysisStatus.PENDING,
            created_at=datetime.now(UTC)
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        # Start analysis task
        task = analyze_contract.delay(
            contract_id=contract.id if contract else None,
            analysis_id=analysis.id,
            source_code=source_code
        )
        
        return {
            "analysis_id": analysis.id,
            "task_id": task.id,
            "status": analysis.status
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting contract analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@track_analysis
async def get_analysis_status(
    db: AsyncSession,
    analysis_id: int
) -> Dict[str, Any]:
    """
    Get analysis status.
    
    Args:
        db: Database session
        analysis_id: Analysis ID
        
    Returns:
        Analysis status and results if available
    """
    try:
        # Get analysis from database
        analysis = await db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = analysis.scalar_one_or_none()
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
            
        # Get task status
        task_info = get_task_info(analysis.task_id)
        
        return {
            "analysis_id": analysis.id,
            "task_id": analysis.task_id,
            "status": analysis.status,
            "results": analysis.results,
            "task_status": task_info
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
