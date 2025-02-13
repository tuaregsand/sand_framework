from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
import jwt
import secrets
import logging
from typing import Optional

from api_gateway.core.config import settings
from api_gateway.db import get_db
from api_gateway.models.database import User

# Configure logging
logger = logging.getLogger(__name__)

# API Key header scheme
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(
    api_key: str = Depends(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify API key and return associated user."""
    try:
        # Query user by API key
        result = await db.execute(
            select(User).where(User.api_key == api_key)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )

        return user
    except Exception as e:
        logger.error(f"API key verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying API key"
        )

def generate_api_key() -> str:
    """Generate a new API key."""
    return secrets.token_urlsafe(32)

def create_jwt_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )

def verify_jwt_token(token: str) -> dict:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return secrets.token_urlsafe(32)  # TODO: Implement proper password hashing

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against the provided password."""
    return False  # TODO: Implement proper password verification
