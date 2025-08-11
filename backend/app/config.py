from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from .utils.fix_env_encoding import fix_env_file_encoding


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Settings(BaseSettings):
    # Database
    # Default to SQLite for local development
    DATABASE_URL: str = "sqlite:///./worqly.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OAuth Providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Worqly"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Pydantic Settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


try:
    settings = Settings()
except UnicodeDecodeError:
    # Try to fix encoding and retry once
    fix_env_file_encoding(os.path.join(BACKEND_DIR, ".env"))
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Failed to load settings: {e}") from e