"""
Task queue configuration for async job processing.
"""
from celery import Celery
from celery.result import AsyncResult
from typing import Dict, Any, Optional
import logging
from datetime import datetime, UTC

from api_gateway.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "smart_contract_analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)

def get_task_info(task_id: str) -> Dict[str, Any]:
    """
    Get information about a task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Dict containing task status and result if available
    """
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.status,
        "created": datetime.now(UTC).isoformat()
    }
    
    if result.failed():
        response["error"] = str(result.result)
    elif result.ready():
        response["result"] = result.result
        
    return response
