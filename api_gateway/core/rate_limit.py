"""
Rate limiting configuration.
"""
from typing import Callable
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def rate_limit(
    calls: int = 60,
    period: int = 60
) -> Callable:
    """
    Rate limit decorator.
    
    Args:
        calls: Number of calls allowed
        period: Time period in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @limiter.limit(f"{calls}/{period}s")
        async def wrapper(request: Request, *args, **kwargs):
            try:
                return await func(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Rate limit exceeded: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests"
                )
        return wrapper
    return decorator
