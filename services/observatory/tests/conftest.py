"""Shared test fixtures for Observatory test suite."""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from app import __version__
from app.api.v1 import analyze, batch, examples, health
from app.middleware import AuthMiddleware
from app.models.database import init_database


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    """Test-specific lifespan that skips scheduler to prevent test hangs."""
    # Startup: Initialize database only (skip scheduler)
    await init_database()
    yield
    # Shutdown: Nothing to stop


@pytest.fixture
def test_app():
    """
    Create a test-specific FastAPI app without the cleanup scheduler.

    The scheduler blocks pytest from completing. Tests use this app
    with init_database but without start_cleanup_scheduler.
    """
    app = FastAPI(
        title="Atrium Observatory API",
        description="Conversation analysis service for detecting patterns, themes, and insights",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=test_lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Authentication middleware only (skip rate limiting in tests to avoid cross-test contamination)
    app.add_middleware(AuthMiddleware)

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
def app(test_app):
    """
    Provide test app for contract tests that create their own clients.

    This allows tests to use `from conftest import app` or `app` fixture
    instead of importing from main.py.
    """
    return test_app


@pytest.fixture
async def async_client(test_app):
    """
    Create an async test client for FastAPI app.

    Uses ASGITransport for httpx 0.28+ compatibility.
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
