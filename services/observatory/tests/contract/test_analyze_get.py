"""Contract tests for GET /api/v1/analyze/{id} endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_analyze_get_completed():
    """Test retrieving completed analysis results."""
    # First create an analysis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Retrieve the analysis
        response = await client.get(f"/api/v1/analyze/{analysis_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == analysis_id
    assert "status" in data
    assert data["status"] in ["pending", "processing", "completed", "failed"]


@pytest.mark.asyncio
async def test_analyze_get_response_schema():
    """Test that response matches expected schema."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Hi\nAI: Hello"},
        )
        analysis_id = create_response.json()["id"]

        # Get analysis
        response = await client.get(f"/api/v1/analyze/{analysis_id}")

    assert response.status_code == 200
    data = response.json()

    # Required fields
    assert "id" in data
    assert "status" in data
    assert "created_at" in data

    # Optional fields based on status
    if data["status"] == "completed":
        assert "patterns" in data
        assert "confidence_score" in data
        assert "processing_time" in data
        assert "expires_at" in data


@pytest.mark.asyncio
async def test_analyze_get_with_patterns():
    """Test completed analysis includes pattern data."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create and wait for completion (mock implementation will need this)
        create_response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Question?\nAI: Answer.",
                "options": {"pattern_types": ["dialectic", "sentiment"]},
            },
        )
        analysis_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/analyze/{analysis_id}")

    data = response.json()

    if data["status"] == "completed":
        assert "patterns" in data
        patterns = data["patterns"]

        # Should have requested pattern types
        assert "dialectic" in patterns or data["status"] != "completed"
        assert "sentiment" in patterns or data["status"] != "completed"


@pytest.mark.asyncio
async def test_analyze_get_nonexistent():
    """Test retrieving non-existent analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analyze/nonexistent-id-12345")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_analyze_get_invalid_id_format():
    """Test handling of invalid ID format."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analyze/invalid-format!@#$")

    # Should either be 404 (not found) or 400 (bad format)
    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_analyze_get_confidence_score():
    """Test that confidence score is within valid range."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/analyze/{analysis_id}")

    data = response.json()

    if "confidence_score" in data:
        assert 0.0 <= data["confidence_score"] <= 1.0


@pytest.mark.asyncio
async def test_analyze_get_processing_time():
    """Test that processing_time is present and valid for completed analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Hi\nAI: Hello"},
        )
        analysis_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/analyze/{analysis_id}")

    data = response.json()

    if data["status"] == "completed":
        assert "processing_time" in data
        assert isinstance(data["processing_time"], (int, float))
        assert data["processing_time"] >= 0


@pytest.mark.asyncio
async def test_analyze_get_export_parameter():
    """Test export format parameter (FR-014)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Test JSON export (default)
        response = await client.get(
            f"/api/v1/analyze/{analysis_id}", params={"format": "json"}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyze_get_expired_analysis():
    """Test retrieving expired analysis (after TTL)."""
    # This test would need time manipulation or mocking
    # For now, verify the endpoint structure
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analyze/expired-analysis-id")

    # Should return 404 for expired/non-existent
    assert response.status_code == 404
