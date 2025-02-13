"""
Celery tasks for contract analysis.
"""
from celery import Task
from typing import Dict, Any, Optional
import logging
from datetime import datetime, UTC
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from api_gateway.core.queue import celery_app
from api_gateway.core.config import settings
from api_gateway.models.database import Contract, Analysis, Project
from api_gateway.models.schemas import AnalysisStatus
from agents.contract_analysis.analyzer import SmartContractAnalyzer

logger = logging.getLogger(__name__)

# Create synchronous database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class ContractAnalysisTask(Task):
    """Base task for contract analysis with error handling."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {str(exc)}")
        # Update analysis status in database
        analysis_id = kwargs.get("analysis_id")
        if analysis_id:
            self.update_analysis_status(
                analysis_id=analysis_id,
                status=AnalysisStatus.FAILED,
                error=str(exc)
            )
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")
        
    def update_analysis_status(
        self,
        analysis_id: int,
        status: AnalysisStatus,
        error: Optional[str] = None,
        results: Optional[Dict] = None
    ):
        """Update analysis status in database."""
        with SessionLocal() as db:
            analysis = db.query(Analysis).filter(
                Analysis.id == analysis_id
            ).first()
            
            if analysis:
                analysis.status = status
                if error:
                    analysis.results = {"error": error}
                if results:
                    analysis.results = results
                analysis.updated_at = datetime.now(UTC)
                db.commit()

@celery_app.task(
    bind=True,
    base=ContractAnalysisTask,
    name="analyze_contract",
    max_retries=3,
    soft_time_limit=1800  # 30 minutes
)
def analyze_contract(
    self,
    contract_id: int,
    analysis_id: int,
    source_code: str
) -> Dict[str, Any]:
    """
    Analyze a smart contract.
    
    Args:
        contract_id: Contract ID
        analysis_id: Analysis ID
        source_code: Contract source code
        
    Returns:
        Analysis results
    """
    try:
        # Initialize analyzer
        analyzer = SmartContractAnalyzer(source_code)
        
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
        
        # Update analysis in database
        self.update_analysis_status(
            analysis_id=analysis_id,
            status=AnalysisStatus.COMPLETED,
            results=results
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error analyzing contract {contract_id}: {str(e)}")
        # Retry task
        self.retry(exc=e, countdown=60 * 5)  # Retry in 5 minutes
