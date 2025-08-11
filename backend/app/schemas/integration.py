from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class IntegrationBase(BaseModel):
    provider: str = Field(..., description="gmail, slack, sheets, etc.")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class IntegrationCreate(IntegrationBase):
    config: Optional[Dict[str, Any]] = None


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class IntegrationResponse(IntegrationBase):
    id: int
    user_id: int
    is_active: bool
    config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OAuthTokenResponse(BaseModel):
    id: int
    integration_id: int
    token_type: str
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    is_valid: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None


class OAuthUrlResponse(BaseModel):
    auth_url: str
    state: str 