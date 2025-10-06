"""
Contract tests for cached examples endpoint.

Test T006: GET /examples/{id} contract validation.
These tests MUST fail initially (TDD approach).
"""

from fastapi.testclient import TestClient


def test_example_endpoint_returns_json_for_valid_id():
    """T006: Test GET /examples/dialectic-simple returns 200 with JSON."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/examples/dialectic-simple")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


def test_example_response_has_conversation_and_analysis():
    """T006: Test example response contains required fields."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/examples/dialectic-simple")

    assert response.status_code == 200
    data = response.json()
    assert "conversation" in data
    assert "analysis" in data
    assert isinstance(data["conversation"], list)
    assert isinstance(data["analysis"], dict)


def test_example_endpoint_returns_404_for_invalid_id():
    """T006: Test GET /examples/nonexistent returns 404."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/examples/nonexistent-example")

    assert response.status_code == 404
