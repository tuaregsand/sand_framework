"""
Monitoring and telemetry configuration.
"""
import logging
from functools import wraps
from typing import Callable, Any
from datetime import datetime, UTC
import sentry_sdk
from prometheus_client import Counter, Histogram, start_http_server
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api_gateway.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
ANALYSIS_COUNTER = Counter(
    'contract_analysis_total',
    'Total number of contract analyses',
    ['status']
)
ANALYSIS_DURATION = Histogram(
    'contract_analysis_duration_seconds',
    'Time spent analyzing contracts',
    ['type']
)

def setup_monitoring(app):
    """Setup monitoring for the application."""
    # Configure Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    
    # Configure OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Start Prometheus metrics server
    start_http_server(settings.METRICS_PORT)
    
    logger.info("Monitoring setup completed")

def track_analysis(func: Callable) -> Callable:
    """Decorator to track contract analysis metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = datetime.now(UTC)
        try:
            result = await func(*args, **kwargs)
            ANALYSIS_COUNTER.labels(status="success").inc()
            return result
        except Exception as e:
            ANALYSIS_COUNTER.labels(status="error").inc()
            raise
        finally:
            duration = (datetime.now(UTC) - start_time).total_seconds()
            ANALYSIS_DURATION.labels(
                type=func.__name__
            ).observe(duration)
    
    return wrapper
