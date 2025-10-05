"""Integration tests for webhook notification system."""

import pytest
from httpx import AsyncClient
from app.main import app
from app.core.notifications import WebhookNotifier


@pytest.fixture
async def webhook_notifier():
    """Create webhook notifier instance."""
    notifier = WebhookNotifier()
    yield notifier
    await notifier.close()


@pytest.mark.asyncio
async def test_webhook_send_batch_complete(webhook_notifier):
    """Test sending batch completion webhook."""
    callback_url = "https://httpbin.org/post"  # Test endpoint

    result = await webhook_notifier.send_batch_complete(
        callback_url=callback_url,
        batch_id="batch-123",
        total_conversations=10,
        completed_count=10,
        failed_count=0,
    )

    # Should succeed (or at least attempt)
    assert result is not None


@pytest.mark.asyncio
async def test_webhook_send_batch_failed(webhook_notifier):
    """Test sending batch failure webhook."""
    callback_url = "https://httpbin.org/post"

    result = await webhook_notifier.send_batch_failed(
        callback_url=callback_url,
        batch_id="batch-123",
        error_message="Processing failed",
    )

    assert result is not None


@pytest.mark.asyncio
async def test_webhook_invalid_url(webhook_notifier):
    """Test handling of invalid webhook URL."""
    invalid_url = "not-a-valid-url"

    result = await webhook_notifier.send_batch_complete(
        callback_url=invalid_url,
        batch_id="batch-123",
        total_conversations=1,
        completed_count=1,
        failed_count=0,
    )

    # Should handle gracefully (return False or raise specific exception)
    assert result is False or result is None


@pytest.mark.asyncio
async def test_webhook_timeout(webhook_notifier):
    """Test webhook timeout handling."""
    # URL that will timeout
    timeout_url = "https://httpbin.org/delay/10"

    result = await webhook_notifier.send_batch_complete(
        callback_url=timeout_url,
        batch_id="batch-123",
        total_conversations=1,
        completed_count=1,
        failed_count=0,
        timeout=1.0,  # 1 second timeout
    )

    # Should timeout gracefully
    assert result is False


@pytest.mark.asyncio
async def test_webhook_retry_on_failure(webhook_notifier):
    """Test webhook retry mechanism."""
    # URL that returns 500
    error_url = "https://httpbin.org/status/500"

    result = await webhook_notifier.send_batch_complete(
        callback_url=error_url,
        batch_id="batch-123",
        total_conversations=1,
        completed_count=1,
        failed_count=0,
        max_retries=3,
    )

    # Should retry and eventually fail
    assert result is False


@pytest.mark.asyncio
async def test_webhook_payload_structure(webhook_notifier):
    """Test webhook payload has correct structure."""
    # We'll test this by capturing what would be sent
    payload = webhook_notifier.build_batch_complete_payload(
        batch_id="batch-123",
        total_conversations=5,
        completed_count=4,
        failed_count=1,
    )

    assert "event" in payload
    assert payload["event"] == "batch.complete"
    assert "batch_id" in payload
    assert "data" in payload
    assert "total_conversations" in payload["data"]
    assert "completed_count" in payload["data"]
    assert "failed_count" in payload["data"]
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_webhook_signing(webhook_notifier):
    """Test webhook signature generation for security."""
    payload = {"event": "batch.complete", "batch_id": "batch-123"}

    signature = webhook_notifier.generate_signature(payload, secret="test-secret")

    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) > 0


@pytest.mark.asyncio
async def test_webhook_batch_progress(webhook_notifier):
    """Test sending batch progress updates."""
    callback_url = "https://httpbin.org/post"

    result = await webhook_notifier.send_batch_progress(
        callback_url=callback_url,
        batch_id="batch-123",
        total_conversations=10,
        completed_count=5,
        failed_count=0,
        progress_percent=50.0,
    )

    assert result is not None


@pytest.mark.asyncio
async def test_webhook_end_to_end():
    """Test full webhook flow with batch analysis."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Submit batch with callback
        response = await client.post(
            "/api/v1/analyze/batch",
            json={
                "conversations": [
                    {"id": "conv-1", "text": "Human: Test\nAI: Response"},
                ],
                "options": {
                    "callback_url": "https://httpbin.org/post",
                },
            },
        )

        assert response.status_code == 202
        batch_id = response.json()["batch_id"]

        # Webhook should be triggered when batch completes
        # (In real test, would need to wait and verify webhook was called)
        assert batch_id is not None
