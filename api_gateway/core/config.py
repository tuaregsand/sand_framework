from typing import List, Optional
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
from urllib.parse import urlparse

class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden by environment variables with the same name.
    """
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_VERSION: str = "1.0.0"
    API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = ENVIRONMENT == "development"
    TESTING: Optional[bool] = False
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = DEBUG
    
    @property
    def DATABASE_HOST(self) -> str:
        """Extract database host from DATABASE_URL."""
        parsed = urlparse(self.DATABASE_URL)
        return parsed.hostname or "localhost"
    
    # Redis and Celery
    REDIS_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10
    BROKER_URL: str = "redis://localhost:6379/0"
    RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Contract Analysis
    MAX_CONTRACT_SIZE_KB: int = 1024  # 1MB
    MAX_ANALYSIS_TIME_SECONDS: int = 300  # 5 minutes
    ANALYSIS_TIMEOUT_SECONDS: int = 30
    
    # Smart Contract Analysis Settings
    SECURITY_SCAN_ENABLED: bool = True
    GAS_OPTIMIZATION_ENABLED: bool = True
    CODE_QUALITY_CHECK_ENABLED: bool = True
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_ENDPOINT: Optional[str] = None
    
    # Metrics and Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # External Services
    ETHERSCAN_API_KEY: Optional[str] = None
    SOLSCAN_API_KEY: Optional[str] = None
    
    # File Storage
    STORAGE_BACKEND: str = "local"  # Options: local, s3
    STORAGE_PATH: str = "./storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    
    # Cache Settings
    CACHE_TTL_SECONDS: int = 300
    CACHE_BACKEND: str = "memory"  # Options: memory, redis
    
    # Worker Settings
    WORKER_CONCURRENCY: int = 2
    WORKER_MAX_TASKS_PER_CHILD: int = 100
    
    class Config:
        case_sensitive = True
        env_file = None  # Don't try to read from .env file in production

    def get_database_url(self) -> str:
        """Get database URL."""
        return self.DATABASE_URL

    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL if configured."""
        return self.REDIS_URL

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return bool(self.TESTING)

@lru_cache()
def get_settings() -> Settings:
    """Create cached instance of settings."""
    return Settings()

# Global instance
settings = get_settings()
