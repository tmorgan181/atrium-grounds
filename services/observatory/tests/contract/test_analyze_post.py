"""Contract tests for POST /api/v1/analyze endpoint."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_analyze_post_success():
    """Test successful conversation analysis request."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Hello\nAI: Hi there!",
                "options": {
                    "pattern_types": ["dialectic", "sentiment"],
                    "include_insights": True,
                },
            },
        )

    assert response.status_code == 202  # Accepted for async processing
    data = response.json()

    assert "id" in data
    assert "status" in data
    assert data["status"] in ["pending", "processing"]


@pytest.mark.asyncio
async def test_analyze_post_minimal_request():
    """Test analysis with minimal required fields."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_analyze_post_with_callback():
    """Test analysis with callback URL."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Question?\nAI: Answer.",
                "options": {"callback_url": "https://example.com/webhook"},
            },
        )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_analyze_post_empty_conversation():
    """Test validation of empty conversation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze", json={"conversation_text": ""}
        )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_analyze_post_missing_conversation():
    """Test validation when conversation_text is missing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/analyze", json={})

    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_analyze_post_too_long_conversation():
    """Test validation of conversation exceeding max length."""
    long_text = "A" * 15000  # Exceeds 10K limit

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze", json={"conversation_text": long_text}
        )

    assert response.status_code == 400
    data = response.json()
    assert "length" in data["detail"].lower()


@pytest.mark.asyncio
async def test_analyze_post_injection_attempt():
    """Test validation blocks injection attempts."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "'; DROP TABLE conversations; --"},
        )

    assert response.status_code == 400
    data = response.json()
    assert "injection" in data["detail"].lower() or "invalid" in data["detail"].lower()


@pytest.mark.asyncio
async def test_analyze_post_invalid_pattern_types():
    """Test validation of invalid pattern types."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Hi\nAI: Hello",
                "options": {"pattern_types": ["invalid_pattern"]},
            },
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_post_response_schema():
    """Test that response matches expected schema."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )

    assert response.status_code == 202
    data = response.json()

    # Check required fields
    assert "id" in data
    assert "status" in data
    assert "created_at" in data

    # Validate types
    assert isinstance(data["id"], str)
    assert isinstance(data["status"], str)


@pytest.mark.asyncio
async def test_analyze_post_rate_limit_headers():
    """Test that rate limit headers are present."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Hi\nAI: Hello"},
        )

    # Rate limiting headers (will be added in Phase 2)
    # For now, just verify request succeeds
    assert response.status_code == 202
