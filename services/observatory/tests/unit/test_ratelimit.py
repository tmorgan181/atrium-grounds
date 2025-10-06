"""Unit tests for rate limiting."""

import time

import pytest

from app.core.config import settings
from app.middleware.ratelimit import RateLimiter, TierLimits


def test_tier_limits_public():
    """Test public tier limits match configuration."""
    limits = TierLimits.PUBLIC
    assert limits["requests_per_minute"] == settings.rate_limit_public
    assert limits["requests_per_day"] == 500


def test_tier_limits_api_key():
    """Test API key tier limits match configuration."""
    limits = TierLimits.API_KEY
    assert limits["requests_per_minute"] == settings.rate_limit_api_key
    assert limits["requests_per_day"] == 5000


def test_tier_limits_partner():
    """Test partner tier limits match configuration."""
    limits = TierLimits.PARTNER
    assert limits["requests_per_minute"] == settings.rate_limit_partner
    assert limits["requests_per_day"] == 50000


@pytest.mark.asyncio
async def test_rate_limiter_allow_within_limit():
    """Test rate limiter allows requests within limit."""
    limiter = RateLimiter(redis_url=None)  # Use in-memory for testing

    # Should allow first request
    result = await limiter.check_rate_limit("test_key", tier="public")
    assert result["allowed"] is True
    assert result["remaining"] >= 0


@pytest.mark.asyncio
async def test_rate_limiter_block_over_limit():
    """Test rate limiter blocks requests over limit."""
    limiter = RateLimiter(redis_url=None)

    # Make requests up to limit
    limit = settings.rate_limit_public
    for i in range(limit):
        result = await limiter.check_rate_limit("test_key_2", tier="public")
        assert result["allowed"] is True

    # Next request should be blocked
    result = await limiter.check_rate_limit("test_key_2", tier="public")
    assert result["allowed"] is False
    assert result["retry_after"] > 0


@pytest.mark.asyncio
async def test_rate_limiter_different_tiers():
    """Test different tiers have different limits."""
    limiter = RateLimiter(redis_url=None)

    # Public tier
    public_limit = settings.rate_limit_public
    for i in range(public_limit):
        result = await limiter.check_rate_limit("public_key", tier="public")
        assert result["allowed"] is True
    result = await limiter.check_rate_limit("public_key", tier="public")
    assert result["allowed"] is False

    # API key tier
    api_key_limit = settings.rate_limit_api_key
    for i in range(api_key_limit):
        result = await limiter.check_rate_limit("api_key", tier="api_key")
        assert result["allowed"] is True
    result = await limiter.check_rate_limit("api_key", tier="api_key")
    assert result["allowed"] is False


@pytest.mark.asyncio
async def test_rate_limiter_reset_headers():
    """Test rate limiter provides reset timestamp."""
    limiter = RateLimiter(redis_url=None)

    result = await limiter.check_rate_limit("test_key_3", tier="public")

    assert "reset_at" in result
    assert result["reset_at"] > time.time()
    assert result["limit"] == settings.rate_limit_public
    assert result["remaining"] == settings.rate_limit_public - 1  # After first request


@pytest.mark.asyncio
async def test_rate_limiter_separate_keys():
    """Test different keys have separate rate limits."""
    limiter = RateLimiter(redis_url=None)

    # Use up limit for key1
    limit = settings.rate_limit_public
    for i in range(limit):
        await limiter.check_rate_limit("key1", tier="public")

    # key2 should still have full limit
    result = await limiter.check_rate_limit("key2", tier="public")
    assert result["allowed"] is True
    assert result["remaining"] == limit - 1
