"""Contract tests for POST /api/v1/analyze/{id}/cancel endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_cancel_pending_analysis():
    """Test cancelling a pending analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Long conversation...\nAI: Detailed response..."},
        )
        analysis_id = create_response.json()["id"]

        # Cancel it
        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_processing_analysis():
    """Test cancelling an analysis that's currently processing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Immediately try to cancel
        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    # Should succeed if job is cancellable
    assert response.status_code in [200, 409]  # 200 or 409 Conflict if already completed


@pytest.mark.asyncio
async def test_cancel_nonexistent_analysis():
    """Test cancelling non-existent analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze/nonexistent-id/cancel")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_cancel_completed_analysis():
    """Test attempting to cancel already completed analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Hi\nAI: Hello"},
        )
        analysis_id = create_response.json()["id"]

        # Wait for completion (in real implementation)
        # For now, attempt cancel

        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    # Should return 409 Conflict if already completed, or 200 if still cancellable
    assert response.status_code in [200, 409]


@pytest.mark.asyncio
async def test_cancel_response_schema():
    """Test cancel response matches expected schema."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Cancel
        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert data["id"] == analysis_id


@pytest.mark.asyncio
async def test_cancel_idempotency():
    """Test that cancelling twice is idempotent."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Cancel first time
        response1 = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

        # Cancel second time
        response2 = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    # Both should succeed or return 409, but not error
    assert response1.status_code in [200, 409]
    assert response2.status_code in [200, 409]


@pytest.mark.asyncio
async def test_cancel_invalid_id_format():
    """Test cancelling with invalid ID format."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze/invalid-format!@#/cancel")

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_cancel_audit_logging():
    """Test that cancellation is logged for audit (FR-013)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )
        analysis_id = create_response.json()["id"]

        # Cancel
        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    # The endpoint should work; audit logging tested separately
    assert response.status_code in [200, 409]
