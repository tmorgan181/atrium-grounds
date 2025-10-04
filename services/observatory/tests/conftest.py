"""Shared test fixtures for Observatory test suite."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def async_client():
    """
    Create an async test client for FastAPI app.

    Uses ASGITransport for httpx 0.28+ compatibility.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
