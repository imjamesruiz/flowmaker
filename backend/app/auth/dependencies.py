from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.jwt_service import JWTService
from app.config import settings
from jose import jwk, jwt
from jose.utils import base64url_decode
import httpx
from functools import lru_cache
from typing import Dict, Any, Optional

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.

    If USE_SUPABASE_AUTH is enabled, validate Supabase JWT via JWKS.
    Otherwise, use internal JWT validation.
    """
    token = credentials.credentials
    if settings.USE_SUPABASE_AUTH:
        user = validate_supabase_token_and_get_user(db, token)
    else:
        user = JWTService.validate_token(db, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not verified"
        )
    return current_user 


@lru_cache(maxsize=1)
def _jwks_cache() -> Dict[str, Any]:
    return {}


def _get_supabase_jwks_url() -> Optional[str]:
    if settings.SUPABASE_JWKS_URL:
        return settings.SUPABASE_JWKS_URL
    if settings.SUPABASE_URL:
        return settings.SUPABASE_URL.rstrip('/') + "/auth/v1/.well-known/jwks.json"
    return None


def _get_jwks() -> Dict[str, Any]:
    cache = _jwks_cache()
    if 'jwks' in cache:
        return cache['jwks']
    jwks_url = _get_supabase_jwks_url()
    if not jwks_url:
        raise HTTPException(status_code=500, detail="Supabase JWKS URL not configured")
    with httpx.Client(timeout=5.0) as client:
        resp = client.get(jwks_url)
        resp.raise_for_status()
        cache['jwks'] = resp.json()
        return cache['jwks']


def _verify_with_jwks(token: str) -> Dict[str, Any]:
    jwks = _get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers.get('kid')
    key = next((k for k in jwks.get('keys', []) if k.get('kid') == kid), None)
    if not key:
        # Refresh cache and try once more
        _jwks_cache().pop('jwks', None)
        jwks = _get_jwks()
        key = next((k for k in jwks.get('keys', []) if k.get('kid') == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
    # jose jwt.decode will verify signature using public key
    audience = settings.SUPABASE_AUDIENCE
    issuer = settings.SUPABASE_ISSUER or (settings.SUPABASE_URL.rstrip('/') + '/auth/v1') if settings.SUPABASE_URL else None
    options = {"verify_aud": bool(audience)}
    return jwt.decode(token, key, algorithms=[key.get('alg', 'RS256')], audience=audience, issuer=issuer, options=options)


def validate_supabase_token_and_get_user(db: Session, token: str) -> Optional[User]:
    try:
        payload = _verify_with_jwks(token)
        email = payload.get('email') or payload.get('user_metadata', {}).get('email')
        user_id = payload.get('sub')
        if not user_id:
            return None
        user = db.query(User).filter(User.email == email).first() if email else None
        if not user:
            # create a local user record if it doesn't exist
            user = User(email=email or f"user_{user_id}@example.com", full_name=None, is_active=True, is_verified=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        return None