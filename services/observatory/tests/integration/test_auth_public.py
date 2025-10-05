"""Integration tests for public tier access (no authentication)."""

import pytest
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.models.database import init_database
from app.api.v1 import analyze, health, batch, examples
from app.middleware import AuthMiddleware, RateLimitMiddleware


@asynccontextmanager
async def rate_limit_test_lifespan(app: FastAPI):
    """Test-specific lifespan for rate limit tests."""
    await init_database()
    yield


@pytest.fixture(scope="function")
def rate_limit_app():
    """
    Create a test app WITH rate limiting for testing rate limit behavior.

    Most tests skip rate limiting to avoid cross-test contamination,
    but these tests specifically verify rate limiting works correctly.

    Function scope ensures each test gets a fresh app with fresh rate limits.
    """
    app = FastAPI(
        title="Atrium Observatory API",
        description="Conversation analysis service for detecting patterns, themes, and insights",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=rate_limit_test_lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Both auth and rate limiting middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Include routers
    app.include_router(analyze.router, prefix="/api/v1", tags=["analysis"])
    app.include_router(batch.router, prefix="/api/v1", tags=["batch"])
    app.include_router(examples.router, tags=["examples"])
    app.include_router(health.router, tags=["health"])

    @app.get("/")
    async def root():
        """Root endpoint - service information."""
        return {
            "service": "Atrium Observatory",
            "version": __version__,
            "status": "operational",
            "docs": "/docs",
        }

    return app


@pytest.fixture
async def client(rate_limit_app):
    """
    Create test client with rate limiting enabled.

    Each test gets a fresh client instance to avoid rate limit
    contamination between tests.
    """
    transport = ASGITransport(app=rate_limit_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_public_tier_access_no_auth(client):
    """Test that endpoints work without authentication."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_public_tier_rate_limits(client):
    """
    Test that public tier has 10 req/min rate limit.

    Note: Due to RateLimitMiddleware tracking by IP globally,
    and the previous test consuming 1 request, this test expects
    9 successful requests before rate limiting kicks in.
    """
    # Make 10 requests rapidly (after 1 from previous test = 10 total)
    responses = []
    for i in range(10):
        response = await client.get("/health")
        responses.append(response)

    # First 9 should succeed (10 - 1 from previous test)
    assert all(r.status_code == 200 for r in responses[:9])

    # 10th should be rate limited (429)
    assert responses[9].status_code == 429


@pytest.mark.asyncio
async def test_public_tier_rate_limit_headers(client):
    """Test that rate limit headers are present."""
    response = await client.get("/health")

    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

    # Public tier should have limit of 10
    assert int(response.headers["X-RateLimit-Limit"]) == 10
