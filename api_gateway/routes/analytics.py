from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy import select

from api_gateway.core.security import verify_api_key
from api_gateway.db import get_db
from api_gateway.models import schemas
from api_gateway.models.database import User, Alert
from api_gateway.services.market import (
    get_current_price,
    get_market_sentiment,
    get_technical_indicators,
    analyze_market_trends
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get(
    "/price",
    response_model=schemas.PriceResponse,
    summary="Get current SOL price",
    description="Retrieve the current price of SOL in USD with optional historical data"
)
async def get_price(
    include_history: bool = False,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.PriceResponse:
    """Get current SOL price."""
    try:
        price_data = await get_current_price(include_history)
        return schemas.PriceResponse(
            price_usd=price_data["price"],
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error fetching price: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching price data"
        )

@router.get(
    "/sentiment",
    response_model=schemas.SentimentResponse,
    summary="Get market sentiment",
    description="Analyze current market sentiment using social media and news sources"
)
async def get_sentiment(
    sources: Optional[List[str]] = None,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> schemas.SentimentResponse:
    """Get market sentiment analysis."""
    try:
        sentiment_data = await get_market_sentiment(sources)
        return schemas.SentimentResponse(
            sentiment_score=sentiment_data["score"],
            confidence=sentiment_data["confidence"],
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing market sentiment"
        )

@router.get(
    "/alerts",
    response_model=List[schemas.Alert],
    summary="Get user alerts",
    description="Retrieve all active alerts for the authenticated user"
)
async def get_alerts(
    severity: Optional[schemas.SecuritySeverity] = None,
    limit: int = 10,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> List[schemas.Alert]:
    """Get user alerts."""
    try:
        # Analyze market trends and generate alerts
        trends = await analyze_market_trends()
        
        # Create alerts based on trends
        alerts = []
        for trend in trends:
            alert = Alert(
                user_id=user.id,
                type=trend["type"],
                severity=trend["severity"],
                message=trend["message"],
                metadata=trend.get("metadata", {})
            )
            db.add(alert)
        
        await db.commit()
        
        # Query alerts
        query = select(Alert).where(Alert.user_id == user.id)
        if severity:
            query = query.where(Alert.severity == severity)
        query = query.order_by(Alert.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return [schemas.Alert.from_orm(alert) for alert in alerts]
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching alerts"
        )

@router.post(
    "/alerts/settings",
    response_model=dict,
    summary="Update alert settings",
    description="Update alert settings for the authenticated user"
)
async def update_alert_settings(
    settings: dict,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Update user's alert settings."""
    try:
        # Update user's alert settings in database
        user.alert_settings = settings
        await db.commit()
        return {"status": "success", "message": "Alert settings updated"}
    except Exception as e:
        logger.error(f"Error updating alert settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating alert settings"
        )
