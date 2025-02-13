import os
from celery import Celery
from agents.web3_agent import Web3DevAgent
from agents.analytics_agent import AnalyticsAgent
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "agents",
    broker=os.getenv("BROKER_URL"),
    backend=os.getenv("RESULT_BACKEND")
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "agents.tasks.dev_*": {"queue": "web3_agent_queue"},
        "agents.tasks.analytics_*": {"queue": "analytics_agent_queue"}
    },
    task_annotations={
        "*": {
            "rate_limit": "10/m"  # Default rate limit
        }
    }
)

# Initialize agents
web3_agent = Web3DevAgent()
analytics_agent = AnalyticsAgent()

# Web3 Development Tasks
@celery_app.task(name="agents.tasks.dev_answer_question")
async def task_answer_dev_question(question: str) -> str:
    """Handle development questions through Web3 agent."""
    try:
        return await web3_agent.answer_dev_question(question)
    except Exception as e:
        logger.error(f"Error in dev_answer_question task: {str(e)}")
        raise

@celery_app.task(name="agents.tasks.dev_create_project")
async def task_create_project(
    name: str,
    description: str = None,
    framework: str = None
) -> dict:
    """Create a new Solana project."""
    try:
        return await web3_agent.create_project(name, description, framework)
    except Exception as e:
        logger.error(f"Error in create_project task: {str(e)}")
        raise

# Analytics Tasks
@celery_app.task(name="agents.tasks.analytics_get_price")
async def task_get_price() -> dict:
    """Get current Solana price."""
    try:
        return await analytics_agent.get_current_price()
    except Exception as e:
        logger.error(f"Error in get_price task: {str(e)}")
        raise

@celery_app.task(name="agents.tasks.analytics_get_sentiment")
async def task_get_sentiment() -> dict:
    """Get current Solana sentiment analysis."""
    try:
        return await analytics_agent.get_current_sentiment()
    except Exception as e:
        logger.error(f"Error in get_sentiment task: {str(e)}")
        raise

@celery_app.task(name="agents.tasks.analytics_generate_alerts")
async def task_generate_alerts() -> list:
    """Generate alerts based on price and sentiment analysis."""
    try:
        return await analytics_agent.generate_alerts()
    except Exception as e:
        logger.error(f"Error in generate_alerts task: {str(e)}")
        raise

# Periodic Tasks
@celery_app.task(name="agents.tasks.periodic_update_analytics")
async def task_periodic_update_analytics():
    """Update analytics data periodically."""
    try:
        # Update price
        await task_get_price.delay()
        
        # Update sentiment
        await task_get_sentiment.delay()
        
        # Generate alerts
        alerts = await task_generate_alerts.delay()
        
        return {
            "status": "success",
            "alerts_generated": len(alerts) if alerts else 0
        }
    except Exception as e:
        logger.error(f"Error in periodic_update_analytics task: {str(e)}")
        raise

# Configure periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks."""
    # Update analytics every 5 minutes
    sender.add_periodic_task(
        300.0,
        task_periodic_update_analytics.s(),
        name="update_analytics_every_5_minutes"
    )
