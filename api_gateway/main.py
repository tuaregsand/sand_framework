from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import uvicorn
from datetime import datetime, UTC
import logging
from typing import Dict, Any

from api_gateway.core.config import settings
from api_gateway.core.security import verify_api_key
from api_gateway.routes import analytics, devagent, system
from api_gateway.routes.metrics import router as metrics_router
from api_gateway.db import init_db
from api_gateway.models import schemas
from api_gateway.core.monitoring import setup_monitoring

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Contract Analysis Platform",
    description="A comprehensive platform for analyzing smart contracts and providing development assistance",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key security scheme
api_key_header = APIKeyHeader(name="X-API-Key")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Initializing services...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
        # Setup monitoring after database initialization
        setup_monitoring(app)
        logger.info("Monitoring setup completed")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down services...")

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": app.version
    }

@app.get("/metrics")
async def metrics(api_key: str = Depends(verify_api_key)) -> Dict[str, Any]:
    """System metrics endpoint."""
    return {
        "api_requests_total": 0,  # TODO: Implement metrics collection
        "analysis_jobs_total": 0,
        "active_users": 0,
        "timestamp": datetime.now(UTC).isoformat()
    }

# Include routers
app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    devagent.router,
    prefix="/api/v1",
    tags=["Development"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    system.router,
    prefix="/api/v1",
    tags=["System"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    metrics_router,
    prefix="/api/v1",
    tags=["Metrics"],
    dependencies=[Depends(verify_api_key)]
)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(UTC).isoformat()
        }
    )

# Export the app for ASGI servers
app = app
