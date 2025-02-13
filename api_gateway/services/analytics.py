"""
Analytics service for processing and analyzing smart contracts.
"""
from typing import Dict, List, Optional
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from api_gateway.models.database import Analysis, Contract, Project
from api_gateway.models.schemas import AnalysisStatus, ContractAnalysisResponse
from agents.contract_analysis.analyzer import SmartContractAnalyzer

async def start_contract_analysis(
    db: AsyncSession,
    contract_id: int,
    project_id: int
) -> Analysis:
    """Start a new contract analysis."""
    analysis = Analysis(
        contract_id=contract_id,
        project_id=project_id,
        status=AnalysisStatus.PENDING
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

async def get_analysis_status(
    db: AsyncSession,
    analysis_id: int
) -> Optional[Analysis]:
    """Get the status of an analysis."""
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    return result.scalar_one_or_none()

async def update_analysis_results(
    db: AsyncSession,
    analysis_id: int,
    results: Dict,
    status: AnalysisStatus = AnalysisStatus.COMPLETED
) -> Analysis:
    """Update the results of an analysis."""
    stmt = (
        update(Analysis)
        .where(Analysis.id == analysis_id)
        .values(
            results=results,
            status=status,
            updated_at=datetime.now(UTC)
        )
    )
    await db.execute(stmt)
    await db.commit()
    
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    return result.scalar_one()

async def get_contract_analyses(
    db: AsyncSession,
    contract_id: int
) -> List[Analysis]:
    """Get all analyses for a contract."""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.contract_id == contract_id)
        .order_by(Analysis.created_at.desc())
    )
    return result.scalars().all()

async def get_project_analyses(
    db: AsyncSession,
    project_id: int
) -> List[Analysis]:
    """Get all analyses for a project."""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.project_id == project_id)
        .order_by(Analysis.created_at.desc())
    )
    return result.scalars().all()

async def analyze_contract_metrics(
    db: AsyncSession,
    contract_id: int,
    project_id: int
) -> ContractAnalysisResponse:
    """Analyze a contract's metrics."""
    # Get contract
    contract_result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = contract_result.scalar_one_or_none()
    if not contract:
        raise ValueError(f"Contract {contract_id} not found")

    # Get project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Create analysis record
    analysis = await start_contract_analysis(db, contract_id, project_id)

    try:
        # Initialize analyzer
        analyzer = SmartContractAnalyzer(contract.source_code)
        
        # Run analysis
        result = analyzer.analyze()
        
        # Format results
        results = {
            "metrics": result.metrics,
            "security": {
                "issues": result.security_issues,
                "risk_score": result.risk_score
            },
            "gas": {
                "optimizations": result.gas_optimizations
            },
            "quality": {
                "issues": result.code_quality_issues,
                "summary": result.summary
            }
        }

        # Update analysis with results
        analysis = await update_analysis_results(db, analysis.id, results)

        return ContractAnalysisResponse(
            analysis_id=analysis.id,
            status=analysis.status,
            results=results
        )

    except Exception as e:
        # Update analysis with error
        await update_analysis_results(
            db,
            analysis.id,
            {"error": str(e)},
            status=AnalysisStatus.FAILED
        )
        raise
