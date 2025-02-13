from typing import List, Optional
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
from urllib.parse import urlparse
import logging
import sys
import json

# Configure root logger to print to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

def debug_env():
    """Debug function to print all environment info"""
    debug_info = {
        "all_env_vars": dict(os.environ),
        "env_var_names": list(os.environ.keys()),
        "jwt_secret_present": "JWT_SECRET" in os.environ,
        "jwt_secret_value_length": len(os.environ.get("JWT_SECRET", "")) if "JWT_SECRET" in os.environ else 0,
        "python_path": sys.path,
        "current_dir": os.getcwd(),
    }
    
    # Print each piece of info separately for better logging
    logger.info("=== DEBUG ENVIRONMENT INFO ===")
    logger.info(f"All environment variable names: {json.dumps(list(os.environ.keys()), indent=2)}")
    logger.info(f"JWT_SECRET present: {debug_info['jwt_secret_present']}")
    logger.info(f"JWT_SECRET length: {debug_info['jwt_secret_value_length']}")
    logger.info(f"Current directory: {debug_info['current_dir']}")
    logger.info(f"Python path: {json.dumps(debug_info['python_path'], indent=2)}")
    logger.info("=== END DEBUG INFO ===")
    
    # Also check for case variations
    possible_names = ["JWT_SECRET", "jwt_secret", "Jwt_Secret", "jwt-secret", "JWT-SECRET"]
    found_vars = [name for name in possible_names if name in os.environ]
    if found_vars:
        logger.info(f"Found JWT secret with these names: {found_vars}")

def fix_database_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// for async support"""
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return url

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_VERSION: str = "1.0.0"
    API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    TESTING: Optional[bool] = False
    
    # Security
    JWT_SECRET: Optional[str] = None  # Make it optional initially
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    @property
    def DATABASE_HOST(self) -> str:
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
    MAX_CONTRACT_SIZE_KB: int = 1024
    MAX_ANALYSIS_TIME_SECONDS: int = 300
    ANALYSIS_TIMEOUT_SECONDS: int = 30
    
    # Smart Contract Analysis Settings
    SECURITY_SCAN_ENABLED: bool = True
    GAS_OPTIMIZATION_ENABLED: bool = True
    CODE_QUALITY_CHECK_ENABLED: bool = True
    
    # Monitoring Settings
    SENTRY_DSN: Optional[str] = None
    OTLP_ENDPOINT: Optional[str] = None
    METRICS_PORT: int = 9090
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_ENDPOINT: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # External Services
    ETHERSCAN_API_KEY: Optional[str] = None
    SOLSCAN_API_KEY: Optional[str] = None
    
    # File Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_PATH: str = "./storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    
    # Cache Settings
    CACHE_TTL_SECONDS: int = 300
    CACHE_BACKEND: str = "memory"
    
    # Worker Settings
    WORKER_CONCURRENCY: int = 2
    WORKER_MAX_TASKS_PER_CHILD: int = 100
    
    class Config:
        case_sensitive = True
        env_file = None
        env_prefix = ""

    def __init__(self, **kwargs):
        # Run debug function before anything else
        debug_env()
        
        # Log all environment variables
        logger.info("=== Environment Variables ===")
        for key in sorted(os.environ.keys()):
            if 'SECRET' in key or 'KEY' in key:
                logger.info(f"{key}: [hidden]")
            else:
                logger.info(f"{key}: {os.environ[key]}")
        logger.info("=== End Environment Variables ===")
        
        # Try to get JWT_SECRET, handling the space issue
        for key in os.environ:
            if key.strip() == 'JWT_SECRET':
                kwargs['JWT_SECRET'] = os.environ[key].strip()
                logger.info("Found JWT_SECRET in environment variables")
                break
        
        # Fix DATABASE_URL if present in environment
        if 'DATABASE_URL' in os.environ:
            os.environ['DATABASE_URL'] = fix_database_url(os.environ['DATABASE_URL'])
            logger.info(f"Using database URL: {os.environ['DATABASE_URL']}")
        
        super().__init__(**kwargs)
        
        # Validate after initialization
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is required but not set")
        
        # Ensure DATABASE_URL is async compatible
        self.DATABASE_URL = fix_database_url(self.DATABASE_URL)

@lru_cache()
def get_settings() -> Settings:
    """Create cached instance of settings."""
    return Settings()

# Global instance
settings = get_settings()
