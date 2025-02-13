from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime, UTC

from api_gateway.core.security import verify_api_key
from api_gateway.db import get_db
from api_gateway.models import schemas
from api_gateway.models.database import User, Contract, Analysis, Project
from api_gateway.services.contract_analysis import start_contract_analysis, get_analysis_status

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.post(
    "/analyze/{contract_id}",
    response_model=schemas.AnalysisResponse,
    summary="Start contract metrics analysis",
    description="Start analyzing metrics for a smart contract"
)
async def analyze_contract_metrics(
    contract_id: int,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.AnalysisResponse:
    """Start contract metrics analysis."""
    try:
        # Get contract
        contract = await db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        contract = contract.scalar_one_or_none()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found"
            )
            
        # Verify user has access to contract
        if contract.project:
            if contract.project.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this contract"
                )
        
        # Start analysis
        result = await start_contract_analysis(
            db=db,
            source_code=contract.source_code,
            project_id=contract.project_id
        )
        
        return schemas.AnalysisResponse(
            analysis_id=result["analysis_id"],
            task_id=result["task_id"],
            status=result["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/result/{analysis_id}",
    response_model=schemas.AnalysisResponse,
    summary="Get metrics analysis result",
    description="Get the result of a metrics analysis"
)
async def get_metrics_result(
    analysis_id: int,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.AnalysisResponse:
    """Get metrics analysis result."""
    try:
        # Get analysis
        analysis = await db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = analysis.scalar_one_or_none()
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
            
        # Verify user has access to analysis
        if analysis.project:
            if analysis.project.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this analysis"
                )
        
        # Get analysis status
        result = await get_analysis_status(db=db, analysis_id=analysis_id)
        
        return schemas.AnalysisResponse(
            analysis_id=result["analysis_id"],
            task_id=result["task_id"],
            status=result["status"],
            results=result["results"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/project/{project_id}",
    response_model=List[schemas.AnalysisResponse],
    summary="Get project metrics",
    description="Get all metrics analyses for a project"
)
async def get_project_metrics(
    project_id: int,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.AnalysisResponse]:
    """Get all metrics for a project."""
    try:
        # Get project
        project = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
            
        # Verify user has access to project
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
        
        # Get all analyses for project
        analyses = await db.execute(
            select(Analysis)
            .where(Analysis.project_id == project_id)
            .order_by(Analysis.created_at.desc())
        )
        analyses = analyses.scalars().all()
        
        # Get status for each analysis
        results = []
        for analysis in analyses:
            status = await get_analysis_status(db=db, analysis_id=analysis.id)
            results.append(schemas.AnalysisResponse(
                analysis_id=status["analysis_id"],
                task_id=status["task_id"],
                status=status["status"],
                results=status["results"]
            ))
            
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
