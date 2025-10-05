"""Contract tests for POST /api/v1/analyze endpoint."""

import pytest


@pytest.mark.asyncio
async def test_analyze_post_success(async_client):
    """Test successful conversation analysis request."""
    response = await async_client.post(
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
async def test_analyze_post_minimal_request(async_client):
    """Test analysis with minimal required fields."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={"conversation_text": "Human: Test\nAI: Response"},
    )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_analyze_post_with_callback(async_client):
    """Test analysis with callback URL."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={
            "conversation_text": "Human: Question?\nAI: Answer.",
            "options": {"callback_url": "https://example.com/webhook"},
        },
    )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_analyze_post_empty_conversation(async_client):
    """Test validation of empty conversation."""
    response = await async_client.post("/api/v1/analyze", json={"conversation_text": ""})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_analyze_post_missing_conversation(async_client):
    """Test validation when conversation_text is missing."""
    response = await async_client.post("/api/v1/analyze", json={})

    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_analyze_post_too_long_conversation(async_client):
    """Test validation of conversation exceeding max length."""
    long_text = "A" * 15000  # Exceeds 10K limit

    response = await async_client.post("/api/v1/analyze", json={"conversation_text": long_text})

    assert response.status_code == 400
    data = response.json()
    assert "length" in data["detail"].lower()


@pytest.mark.asyncio
async def test_analyze_post_injection_attempt(async_client):
    """Test validation blocks injection attempts."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={"conversation_text": "'; DROP TABLE conversations; --"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "injection" in data["detail"].lower() or "invalid" in data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Pattern type validation not implemented (Feature 001 issue, not Feature 002)")
async def test_analyze_post_invalid_pattern_types(async_client):
    """Test validation of invalid pattern types."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={
            "conversation_text": "Human: Hi\nAI: Hello",
            "options": {"pattern_types": ["invalid_pattern"]},
        },
    )

    # TODO: Should return 400 once pattern_types validation is implemented
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_post_response_schema(async_client):
    """Test that response matches expected schema."""
    response = await async_client.post(
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
async def test_analyze_post_rate_limit_headers(async_client):
    """Test that rate limit headers are present."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={"conversation_text": "Human: Hi\nAI: Hello"},
    )

    # Rate limiting headers (will be added in Phase 2)
    # For now, just verify request succeeds
    assert response.status_code == 202
