"""Contract tests for batch analysis endpoints."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_batch_submit_success():
    """Test successful batch analysis submission."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "Human: Hello\nAI: Hi there!"},
                    {"id": "conv-2", "text": "Human: Goodbye\nAI: See you!"},
                ],
                "options": {
                    "pattern_types": ["dialectic", "sentiment"],
                    "callback_url": "https://example.com/webhook",
                },
            },
        )

    assert response.status_code == 202
    data = response.json()

    assert "batch_id" in data
    assert "status" in data
    assert data["status"] == "pending"
    assert "total_conversations" in data
    assert data["total_conversations"] == 2


@pytest.mark.asyncio
async def test_batch_size_validation():
    """Test batch size limit enforcement (FR-011: max 1,000)."""
    # Create 1001 conversations
    conversations = [
        {"id": f"conv-{i}", "text": f"Human: Test {i}\nAI: Response {i}"}
        for i in range(1001)
    ]

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={"conversations": conversations},
        )

    assert response.status_code == 400
    data = response.json()
    assert "batch size" in data["detail"].lower() or "1000" in data["detail"]


@pytest.mark.asyncio
async def test_batch_empty_conversations():
    """Test validation of empty conversation list."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={"conversations": []},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_invalid_conversation():
    """Test validation catches invalid conversations in batch."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "'; DROP TABLE analyses; --"},  # Injection attempt
                ],
            },
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_get_status():
    """Test retrieving batch status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Submit batch
        submit_response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "Human: Test\nAI: Response"},
                ],
            },
        )
        batch_id = submit_response.json()["batch_id"]

        # Get status
        status_response = await client.get(f"/api/v1/analyze/batch/{batch_id}")

    assert status_response.status_code == 200
    data = status_response.json()

    assert data["batch_id"] == batch_id
    assert "status" in data
    assert "total_conversations" in data
    assert "completed_count" in data
    assert "failed_count" in data


@pytest.mark.asyncio
async def test_batch_get_nonexistent():
    """Test retrieving non-existent batch."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analyze/batch/nonexistent-batch-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_batch_with_callback():
    """Test batch submission with webhook callback."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "Human: Test\nAI: Response"},
                ],
                "options": {
                    "callback_url": "https://example.com/webhook",
                },
            },
        )

    assert response.status_code == 202
    data = response.json()
    assert "batch_id" in data


@pytest.mark.asyncio
async def test_batch_response_schema():
    """Test batch response matches expected schema."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "Human: Test\nAI: Response"},
                ],
            },
        )

    assert response.status_code == 202
    data = response.json()

    # Required fields
    assert "batch_id" in data
    assert "status" in data
    assert "total_conversations" in data
    assert "created_at" in data

    # Validate types
    assert isinstance(data["batch_id"], str)
    assert isinstance(data["status"], str)
    assert isinstance(data["total_conversations"], int)
