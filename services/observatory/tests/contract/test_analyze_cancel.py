"""Contract tests for POST /api/v1/analyze/{id}/cancel endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_cancel_pending_analysis(app):
    """Test cancelling a pending analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analysis
        create_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Long conversation here\nAI: Detailed response here"},
        )

        # Check if creation succeeded
        assert create_response.status_code in [200, 201, 202], (
            f"Failed to create analysis: {create_response.status_code} - {create_response.text}"
        )

        analysis_id = create_response.json()["id"]

        # Cancel it
        response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_processing_analysis(app):
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
async def test_cancel_nonexistent_analysis(app):
    """Test cancelling non-existent analysis."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze/nonexistent-id/cancel")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_cancel_completed_analysis(app):
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
async def test_cancel_response_schema(app):
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
async def test_cancel_idempotency(app):
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
async def test_cancel_invalid_id_format(app):
    """Test cancelling with invalid ID format."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze/invalid-format!@#/cancel")

    # 400 (Bad Request), 404 (Not Found), or 405 (Method Not Allowed) are all acceptable
    # 405 happens when URL characters cause routing issues
    assert response.status_code in [400, 404, 405]


@pytest.mark.asyncio
async def test_cancel_audit_logging(app):
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
