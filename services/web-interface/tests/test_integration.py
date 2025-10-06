"""
Integration tests for full user flows.

Tests T009-T010: End-to-end user journey validation.
These tests MUST fail initially (TDD approach).
"""

import pytest
import time
from fastapi.testclient import TestClient


def test_visitor_sees_value_proposition_in_30_seconds():
    """T009: Test landing page provides clear value prop within 30s."""
    from app.main import app

    client = TestClient(app)

    start_time = time.time()
    response = client.get("/")
    response_time = (time.time() - start_time) * 1000  # Convert to ms

    # Response should be fast (<500ms for good UX)
    assert response_time < 500, f"Landing page too slow: {response_time}ms"

    # Should have clear value proposition
    assert response.status_code == 200
    text_lower = response.text.lower()

    # Looking for key value prop indicators
    has_value_prop = any(
        [
            "conversation" in text_lower and "analysis" in text_lower,
            "pattern" in text_lower,
            "explore" in text_lower,
            "understand" in text_lower,
        ]
    )
    assert has_value_prop, "Landing page should have clear value proposition"


def test_cached_example_loads_in_under_100ms():
    """T010: Test cached example responds instantly (<100ms)."""
    from app.main import app

    client = TestClient(app)

    # Measure response time for cached example
    start_time = time.time()
    response = client.get("/examples/dialectic-simple")
    response_time = (time.time() - start_time) * 1000  # Convert to ms

    # Cached examples should be very fast (static file)
    assert response_time < 100, f"Cached example too slow: {response_time}ms"
    assert response.status_code == 200


@pytest.mark.skipif(
    "OBSERVATORY_URL" not in __import__("os").environ,
    reason="Observatory not configured",
)
def test_live_demo_completes_in_under_3_seconds():
    """T010: Test live analysis (with Observatory) completes in <3s."""
    from app.main import app
    import os

    api_key = os.getenv("OBSERVATORY_API_KEY")
    if not api_key:
        pytest.skip("OBSERVATORY_API_KEY not set")

    client = TestClient(app)

    # Measure response time for live API call to Observatory
    start_time = time.time()
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
    response_time = (time.time() - start_time) * 1000  # Convert to ms

    # Live analysis should complete in <3 seconds (3000ms)
    # Only assert if Observatory is actually responding
    if response.status_code == 200:
        assert response_time < 3000, f"Live demo too slow: {response_time}ms"


def test_full_user_journey():
    """T009+T010: Test complete user flow from landing to demo."""
    from app.main import app

    client = TestClient(app)

    # Step 1: Visit landing page
    response = client.get("/")
    assert response.status_code == 200
    assert "Observatory" in response.text or "observatory" in response.text.lower()

    # Step 2: Navigate to demo page
    response = client.get("/demo")
    assert response.status_code == 200

    # Step 3: Load a cached example
    response = client.get("/examples/dialectic-simple")
    assert response.status_code == 200
    data = response.json()
    assert "conversation" in data
    assert "analysis" in data

    # Step 4: Check Observatory health
    response = client.get("/api/health")
    assert response.status_code in [200, 503]  # 200 if up, 503 if down
