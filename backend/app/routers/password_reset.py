from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.password_reset import (
    PasswordResetRequest, 
    PasswordResetVerify, 
    PasswordResetConfirm,
    PasswordResetResponse,
    PasswordResetTokenResponse
)
from app.services.password_reset_service import PasswordResetService

router = APIRouter()


@router.post("/request", response_model=PasswordResetResponse)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request a password reset email"""
    try:
        success = PasswordResetService.send_reset_email(db, request.email)
        
        if success:
            return PasswordResetResponse(
                message="Password reset email sent successfully. Please check your email for the verification code.",
                email=request.email
            )
        else:
            # Don't reveal if email exists or not for security
            return PasswordResetResponse(
                message="If an account with this email exists, a password reset email has been sent.",
                email=request.email
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )


@router.post("/verify", response_model=PasswordResetTokenResponse)
def verify_reset_code(
    request: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """Verify the reset code"""
    try:
        is_valid = PasswordResetService.verify_code(
            db, 
            request.email, 
            request.verification_code
        )
        
        if is_valid:
            return PasswordResetTokenResponse(
                message="Verification code is valid",
                expires_in_minutes=15
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify code"
        )


@router.post("/confirm", response_model=PasswordResetResponse)
def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with new password"""
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Reset password
        success = PasswordResetService.reset_password(
            db,
            request.email,
            request.verification_code,
            request.new_password
        )
        
        if success:
            return PasswordResetResponse(
                message="Password reset successfully. You can now log in with your new password.",
                email=request.email
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
