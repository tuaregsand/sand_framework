from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
import psutil
import platform
from datetime import datetime, timedelta, UTC
from typing import Dict, Any

from api_gateway.core.security import verify_api_key
from api_gateway.core.config import settings
from api_gateway.db import get_db
from api_gateway.models.database import User, Analysis
from api_gateway.models.schemas import AnalysisStatus
from sqlalchemy import func, delete, and_

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/system", tags=["System"])

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="System health check",
    description="Check the health status of all system components"
)
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Check system health."""
    try:
        # Check database connection
        await db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": db_status,
            "api": "healthy"
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "python_version": platform.python_version(),
            "platform": platform.platform()
        }
    }

@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    summary="System metrics",
    description="Get detailed system metrics and statistics"
)
async def get_metrics(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get system metrics."""
    try:
        # Get analysis statistics
        analysis_stats = await db.execute(
            select(
                Analysis.status,
                func.count(Analysis.id).label('count')
            ).group_by(Analysis.status)
        )
        analysis_counts = {
            status.value: count
            for status, count in analysis_stats.all()
        }

        # Get system metrics
        cpu_times = psutil.cpu_times()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "analysis": {
                "total": sum(analysis_counts.values()),
                "by_status": analysis_counts
            },
            "system": {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "times": {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching system metrics"
        )

@router.post(
    "/maintenance/cleanup",
    response_model=Dict[str, Any],
    summary="System cleanup",
    description="Perform system maintenance and cleanup tasks"
)
async def system_cleanup(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Perform system cleanup."""
    try:
        # Clean up old analysis records
        cleanup_date = datetime.now(UTC) - timedelta(days=30)
        await db.execute(
            delete(Analysis).where(
                and_(
                    Analysis.created_at < cleanup_date,
                    Analysis.status.in_([
                        AnalysisStatus.COMPLETED,
                        AnalysisStatus.FAILED
                    ])
                )
            )
        )
        await db.commit()

        return {
            "status": "success",
            "message": "System cleanup completed successfully",
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        logger.error(f"Error during system cleanup: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during system cleanup"
        )

@router.get(
    "/config",
    response_model=Dict[str, Any],
    summary="System configuration",
    description="Get current system configuration settings"
)
async def get_config(
    user: User = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get system configuration."""
    try:
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "api_version": settings.API_VERSION,
            "features": {
                "security_scan": settings.SECURITY_SCAN_ENABLED,
                "gas_optimization": settings.GAS_OPTIMIZATION_ENABLED,
                "code_quality": settings.CODE_QUALITY_CHECK_ENABLED
            },
            "limits": {
                "max_contract_size": settings.MAX_CONTRACT_SIZE_KB,
                "max_analysis_time": settings.MAX_ANALYSIS_TIME_SECONDS,
                "rate_limit": settings.RATE_LIMIT_PER_MINUTE
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching system configuration"
        )
