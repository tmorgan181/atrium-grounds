"""Integration tests for public tier access (no authentication)."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_public_tier_access_no_auth(client):
    """Test that endpoints work without authentication."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_public_tier_rate_limits(client):
    """Test that public tier has 10 req/min rate limit."""
    # Make 11 requests rapidly
    responses = []
    for i in range(11):
        response = await client.get("/health")
        responses.append(response)
    
    # First 10 should succeed
    assert all(r.status_code == 200 for r in responses[:10])
    
    # 11th should be rate limited (429)
    assert responses[10].status_code == 429


@pytest.mark.asyncio
async def test_public_tier_rate_limit_headers(client):
    """Test that rate limit headers are present."""
    response = await client.get("/health")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    
    # Public tier should have limit of 10
    assert int(response.headers["X-RateLimit-Limit"]) == 10
