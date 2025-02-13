from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from datetime import datetime, UTC
from typing import Optional

from api_gateway.core.security import verify_api_key
from api_gateway.db import get_db
from api_gateway.models import schemas
from api_gateway.models.database import User, Project, Contract, Analysis
from api_gateway.services.contract_analysis import analyze_contract
from api_gateway.services.project_manager import create_project_scaffold

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dev", tags=["Web3 Development"])

@router.post(
    "/project/new",
    response_model=schemas.ProjectResult,
    summary="Create new project",
    description="Create a new smart contract project with the specified framework"
)
async def create_new_project(
    project: schemas.ProjectCreate,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.ProjectResult:
    """Create a new smart contract project."""
    try:
        # Create project in database
        db_project = Project(
            name=project.name,
            description=project.description,
            framework=project.framework,
            owner_id=user.id
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)

        # Create project scaffold
        project_path = await create_project_scaffold(
            project.name,
            project.framework,
            db_project.id
        )

        return schemas.ProjectResult(
            result="Project created successfully",
            path=project_path,
            timestamp=datetime.now(UTC)
        )
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating project"
        )

@router.post(
    "/contract/analyze",
    response_model=schemas.AnalysisResult,
    summary="Analyze smart contract",
    description="Perform comprehensive analysis of a smart contract"
)
async def analyze_smart_contract(
    contract_file: UploadFile = File(...),
    project_id: Optional[int] = None,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.AnalysisResult:
    """Analyze a smart contract."""
    try:
        # Read contract content
        content = await contract_file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty contract file"
            )

        # Create contract in database
        contract = Contract(
            name=contract_file.filename,
            source_code=content.decode(),
            project_id=project_id
        )
        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        # Create analysis record
        analysis = Analysis(
            contract_id=contract.id,
            project_id=project_id,
            status=schemas.AnalysisStatus.RUNNING
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        try:
            # Perform analysis
            result = await analyze_contract(content.decode())
            
            # Update analysis record
            analysis.status = schemas.AnalysisStatus.COMPLETED
            analysis.results = result
            await db.commit()

            return schemas.AnalysisResult(**result)
        except Exception as e:
            # Update analysis record with error
            analysis.status = schemas.AnalysisStatus.FAILED
            analysis.error = str(e)
            await db.commit()
            raise

    except Exception as e:
        logger.error(f"Error analyzing contract: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing contract"
        )

@router.get(
    "/analysis/{analysis_id}",
    response_model=schemas.AnalysisResult,
    summary="Get analysis result",
    description="Retrieve the result of a previous contract analysis"
)
async def get_analysis_result(
    analysis_id: int,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.AnalysisResult:
    """Get analysis result by ID."""
    try:
        result = await db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        if analysis.status == schemas.AnalysisStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {analysis.error}"
            )

        if analysis.status != schemas.AnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_102_PROCESSING,
                detail="Analysis still in progress"
            )

        return schemas.AnalysisResult(**analysis.results)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analysis"
        )

@router.post(
    "/ask",
    response_model=schemas.DevAnswer,
    summary="Ask development question",
    description="Ask a development-related question and get an AI-powered answer"
)
async def ask_question(
    question: schemas.DevQuestion,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.DevAnswer:
    """Ask a development question."""
    try:
        # TODO: Implement AI-powered question answering
        return schemas.DevAnswer(
            answer="This feature is coming soon!",
            references=[],
            timestamp=datetime.now(UTC)
        )
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing question"
        )
