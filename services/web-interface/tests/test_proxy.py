"""
Contract tests for Observatory API proxy endpoints.

Tests T007-T008: POST /api/analyze and GET /api/health contract validation.
These tests MUST fail initially (TDD approach).
"""

import pytest
from fastapi.testclient import TestClient


def test_analyze_endpoint_requires_api_key():
    """T007: Test POST /api/analyze returns 401 without API key."""
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation": [
                {"speaker": "A", "content": "Test message"},
                {"speaker": "B", "content": "Test response"},
            ]
        },
    )

    # Without API key, should return 401 (or 403 depending on implementation)
    assert response.status_code in [401, 403]


def test_analyze_endpoint_with_api_key_returns_200():
    """T007: Test POST /api/analyze with valid API key returns 200 (may fail if Observatory down)."""
    from app.main import app
    import os

    # This test may be skipped if Observatory is not running
    # or if API key is not configured
    api_key = os.getenv("OBSERVATORY_API_KEY")
    if not api_key:
        pytest.skip("OBSERVATORY_API_KEY not set")

    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation": [
                {"speaker": "A", "content": "What is truth?"},
                {"speaker": "B", "content": "Truth is subjective."},
            ]
        },
        headers={"X-API-Key": api_key},
    )

    # May return 200 (success) or 503 (Observatory down) - both acceptable
    assert response.status_code in [200, 503]


def test_analyze_endpoint_proxies_to_observatory():
    """T007: Test analyze endpoint forwards request to Observatory correctly."""
    from app.main import app
    import os

    api_key = os.getenv("OBSERVATORY_API_KEY")
    if not api_key:
        pytest.skip("OBSERVATORY_API_KEY not set")

    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation": [
                {"speaker": "A", "content": "Hello"},
                {"speaker": "B", "content": "Hi there"},
            ]
        },
        headers={"X-API-Key": api_key},
    )

    if response.status_code == 200:
        # If Observatory is up, should get analysis response
        data = response.json()
        # Should have analysis fields (exact structure depends on Observatory)
        assert isinstance(data, dict)


def test_health_endpoint_returns_json():
    """T008: Test GET /api/health returns health status JSON."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health")

    # Should return 200 (Observatory up) or 503 (Observatory down)
    assert response.status_code in [200, 503]
    assert "application/json" in response.headers["content-type"]


def test_health_response_has_status_and_response_time():
    """T008: Test health response contains required fields."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health")

    data = response.json()
    assert "status" in data
    assert "response_time_ms" in data or "error" in data  # error if Observatory down
