"""Rate limiting middleware with Redis backend."""

import time
from typing import Dict, Optional
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import log_rate_limit_exceeded


class TierLimits:
    """Rate limit configurations by tier."""

    PUBLIC = {
        "requests_per_minute": settings.rate_limit_public,
        "requests_per_day": 500,
    }

    API_KEY = {
        "requests_per_minute": settings.rate_limit_api_key,
        "requests_per_day": 5000,
    }

    PARTNER = {
        "requests_per_minute": settings.rate_limit_partner,
        "requests_per_day": 50000,
    }

    @classmethod
    def get_limits(cls, tier: str) -> Dict[str, int]:
        """Get rate limits for a tier."""
        if tier == "partner":
            return cls.PARTNER
        elif tier == "api_key":
            return cls.API_KEY
        else:
            return cls.PUBLIC


class RateLimiter:
    """
    Rate limiter with in-memory storage for Phase 2.
    Phase 5 will migrate to Redis for distributed rate limiting.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize rate limiter.

        Args:
            redis_url: Redis connection URL (for Phase 5)
        """
        self.redis_url = redis_url
        self.use_redis = redis_url is not None and redis_url != ""

        # In-memory storage for Phase 2
        # Structure: {key: {"minute": [(timestamp, count)], "day": [(timestamp, count)]}}
        self._memory_store: Dict[str, Dict[str, list]] = defaultdict(
            lambda: {"minute": [], "day": []}
        )

    def _clean_old_entries(self, key: str, now: float) -> None:
        """Remove entries older than their time window."""
        # Clean minute window (60 seconds)
        self._memory_store[key]["minute"] = [
            (ts, count) for ts, count in self._memory_store[key]["minute"] if now - ts < 60
        ]

        # Clean day window (86400 seconds)
        self._memory_store[key]["day"] = [
            (ts, count) for ts, count in self._memory_store[key]["day"] if now - ts < 86400
        ]

    async def check_rate_limit(self, identifier: str, tier: str = "public") -> Dict:
        """
        Check if request is within rate limit.

        Args:
            identifier: Unique identifier (IP address or API key)
            tier: Access tier (public, api_key, partner)

        Returns:
            Dictionary with:
                - allowed: bool
                - limit: int (requests per minute)
                - remaining: int
                - reset_at: float (Unix timestamp)
                - retry_after: int (seconds, if blocked)
        """
        limits = TierLimits.get_limits(tier)
        now = time.time()

        # Clean old entries
        self._clean_old_entries(identifier, now)

        # Count requests in current minute
        minute_requests = sum(count for ts, count in self._memory_store[identifier]["minute"])

        # Check minute limit
        minute_limit = limits["requests_per_minute"]
        reset_at = now + 60

        if minute_requests >= minute_limit:
            return {
                "allowed": False,
                "limit": minute_limit,
                "remaining": 0,
                "reset_at": reset_at,
                "retry_after": int(reset_at - now),
            }

        # Add current request
        self._memory_store[identifier]["minute"].append((now, 1))
        self._memory_store[identifier]["day"].append((now, 1))

        return {
            "allowed": True,
            "limit": minute_limit,
            "remaining": minute_limit - minute_requests - 1,
            "reset_at": reset_at,
            "retry_after": 0,
        }


# Global rate limiter instance
rate_limiter = RateLimiter(redis_url=settings.redis_url if hasattr(settings, "redis_url") else None)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Enforces tier-based rate limits and adds rate limit headers to responses.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and check rate limits."""
        # Get tier from request state (set by AuthMiddleware)
        tier = getattr(request.state, "tier", "public")

        # Generate identifier (IP or API key)
        identifier = getattr(request.state, "api_key", None)
        if not identifier:
            # Use IP address for public tier
            identifier = request.client.host if request.client else "unknown"

        # Check rate limit
        result = await rate_limiter.check_rate_limit(identifier, tier)

        if not result["allowed"]:
            # Log rate limit exceeded
            log_rate_limit_exceeded(
                ip_address=request.client.host if request.client else "unknown",
                tier=tier,
                endpoint=request.url.path,
            )

            # Return 429 Too Many Requests
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": result["limit"],
                    "retry_after": result["retry_after"],
                },
                headers={
                    "X-RateLimit-Limit": str(result["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(result["reset_at"])),
                    "Retry-After": str(result["retry_after"]),
                },
            )

        # Continue processing
        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(result["reset_at"]))

        return response
