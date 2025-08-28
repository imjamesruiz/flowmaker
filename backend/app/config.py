import os
from typing import Optional, List

# Try to import pydantic_settings, fallback to pydantic if not available
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    try:
        from pydantic import BaseSettings
        from pydantic import Field
        # Create a simple SettingsConfigDict equivalent
        class SettingsConfigDict:
            def __init__(self, **kwargs):
                self.env_file = kwargs.get('env_file')
                self.env_file_encoding = kwargs.get('env_file_encoding', 'utf-8')
                self.case_sensitive = kwargs.get('case_sensitive', True)
                self.extra = kwargs.get('extra', 'ignore')
    except ImportError:
        raise ImportError("Please install pydantic: pip install pydantic")

from .utils.fix_env_encoding import fix_env_file_encoding


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Settings(BaseSettings):
    # Database Configuration
    POSTGRES_DB: str = "worqly"
    POSTGRES_USER: str = "worqly_user"
    POSTGRES_PASSWORD: str = "your_secure_password_here"
    DATABASE_URL: str = "sqlite:///./worqly.db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth Providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Worqly"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    VITE_API_BASE_URL: str = "http://localhost:8000/api/v1"
    DEBUG: bool = True
    
    # Monitoring
    GRAFANA_PASSWORD: Optional[str] = None
    
    # Optional: External Services
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


try:
    settings = Settings()
except UnicodeDecodeError:
    # Try to fix encoding and retry once
    fix_env_file_encoding(os.path.join(BACKEND_DIR, ".env"))
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Failed to load settings: {e}") from e