"""
Contract tests for HTML page routes.

Tests T004-T005: Landing page and demo page contract validation.
These tests MUST fail initially (TDD approach).
"""
import pytest
from fastapi.testclient import TestClient


def test_landing_page_returns_html():
    """T004: Test GET / returns 200 with HTML content."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_landing_page_contains_atrium_and_observatory():
    """T004: Test landing page contains 'Atrium' and 'Observatory'."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Atrium" in response.text or "atrium" in response.text.lower()
    assert "Observatory" in response.text or "observatory" in response.text.lower()


def test_landing_page_has_no_technical_jargon():
    """T004: Test landing page avoids technical jargon (Constitution I)."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    # Should not contain technical terms in public-facing content
    jargon_terms = ["FastAPI", "REST", "API endpoint", "JSON schema"]
    for term in jargon_terms:
        assert term not in response.text, f"Found technical jargon: {term}"


def test_demo_page_returns_html():
    """T005: Test GET /demo returns 200 with HTML content."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/demo")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_demo_page_contains_example_buttons():
    """T005: Test demo page contains interactive example elements."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/demo")

    assert response.status_code == 200
    # Should have some form of example selection (buttons, links, cards)
    # Looking for common HTML patterns
    has_examples = (
        "example" in response.text.lower() or
        "demo" in response.text.lower() or
        "try" in response.text.lower()
    )
    assert has_examples, "Demo page should contain example/demo elements"
