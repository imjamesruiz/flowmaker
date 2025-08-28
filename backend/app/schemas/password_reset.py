from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send reset code to")


class PasswordResetVerify(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class PasswordResetConfirm(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")


class PasswordResetResponse(BaseModel):
    message: str
    email: str


class PasswordResetTokenResponse(BaseModel):
    message: str
    expires_in_minutes: int
