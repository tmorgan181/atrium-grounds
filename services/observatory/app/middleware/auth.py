"""API key authentication middleware."""

import hashlib
import secrets
from typing import Optional, Dict

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import log_auth_success, log_auth_failure


# In-memory API key registry for Phase 2
# Phase 5 will move this to database
API_KEY_REGISTRY: Dict[str, str] = {}


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    
    Returns:
        32-character alphanumeric API key
    """
    return secrets.token_urlsafe(24)[:32]


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        SHA256 hash of the API key with salt
    """
    salted = f"{settings.api_key_salt}{api_key}".encode()
    return hashlib.sha256(salted).hexdigest()


def validate_api_key(api_key: Optional[str], registry: Dict[str, str]) -> bool:
    """
    Validate an API key against the registry.
    
    Args:
        api_key: API key to validate
        registry: Dictionary of hashed keys to tier names
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    hashed = hash_api_key(api_key)
    return hashed in registry


def register_api_key(api_key: str, tier: str = "api_key") -> None:
    """
    Register an API key in the in-memory registry.
    
    Args:
        api_key: Plain text API key to register
        tier: Access tier (api_key or partner)
    """
    hashed = hash_api_key(api_key)
    API_KEY_REGISTRY[hashed] = tier


def get_tier_from_api_key(api_key: str) -> str:
    """
    Get the access tier for an API key.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Tier name (api_key or partner)
    """
    hashed = hash_api_key(api_key)
    return API_KEY_REGISTRY.get(hashed, "public")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for API key validation.
    
    Checks Authorization header and sets request.state.tier accordingly:
    - No header: tier = "public"
    - Valid API key: tier = "api_key" or "partner"
    - Invalid API key: returns 401 Unauthorized
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""
        # Get Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        # Default to public tier
        tier = "public"
        api_key = None
        
        # Parse Bearer token
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()
            
            # Validate API key
            if validate_api_key(api_key, API_KEY_REGISTRY):
                tier = get_tier_from_api_key(api_key)
                
                # Log successful auth
                key_prefix = api_key[:8] if len(api_key) >= 8 else api_key
                log_auth_success(api_key_prefix=key_prefix, tier=tier)
            else:
                # Invalid API key
                key_prefix = api_key[:8] if len(api_key) >= 8 else api_key
                log_auth_failure(api_key_prefix=key_prefix, reason="invalid_key")
                
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Set tier in request state for downstream use
        request.state.tier = tier
        request.state.api_key = api_key
        
        # Continue processing
        response = await call_next(request)
        return response


# Helper function to get current tier from request
def get_current_tier(request: Request) -> str:
    """
    Get the current access tier from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tier name (public, api_key, or partner)
    """
    return getattr(request.state, "tier", "public")
