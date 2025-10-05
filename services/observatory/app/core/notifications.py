"""Webhook notification system for batch processing events."""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """
    Sends webhook notifications for batch processing events.

    Events:
    - batch.progress: Periodic progress updates
    - batch.complete: Batch processing completed
    - batch.failed: Batch processing failed

    Payload format follows standard webhook conventions with
    event type, timestamp, and event-specific data.
    """

    def __init__(self, timeout: float = 10.0):
        """
        Initialize webhook notifier.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def send_batch_progress(
        self,
        callback_url: str,
        batch_id: str,
        total_conversations: int,
        completed_count: int,
        failed_count: int,
        progress_percent: float,
    ) -> bool:
        """
        Send batch progress update notification.

        Args:
            callback_url: Webhook endpoint URL
            batch_id: Batch identifier
            total_conversations: Total number of conversations
            completed_count: Number of completed analyses
            failed_count: Number of failed analyses
            progress_percent: Progress percentage (0.0-100.0)

        Returns:
            True if notification sent successfully, False otherwise
        """
        payload = self.build_batch_progress_payload(
            batch_id=batch_id,
            total_conversations=total_conversations,
            completed_count=completed_count,
            failed_count=failed_count,
            progress_percent=progress_percent,
        )

        return await self._send_webhook(callback_url, payload)

    async def send_batch_complete(
        self,
        callback_url: str,
        batch_id: str,
        total_conversations: int,
        completed_count: int,
        failed_count: int,
        timeout: Optional[float] = None,
        max_retries: int = 0,
    ) -> bool:
        """
        Send batch completion notification.

        Args:
            callback_url: Webhook endpoint URL
            batch_id: Batch identifier
            total_conversations: Total number of conversations
            completed_count: Number of successful analyses
            failed_count: Number of failed analyses
            timeout: Request timeout in seconds (overrides default)
            max_retries: Maximum number of retry attempts on failure

        Returns:
            True if notification sent successfully, False otherwise
        """
        payload = self.build_batch_complete_payload(
            batch_id=batch_id,
            total_conversations=total_conversations,
            completed_count=completed_count,
            failed_count=failed_count,
        )

        return await self._send_webhook(callback_url, payload, timeout=timeout, max_retries=max_retries)

    async def send_batch_failed(
        self,
        callback_url: str,
        batch_id: str,
        error_message: str,
    ) -> bool:
        """
        Send batch failure notification.

        Args:
            callback_url: Webhook endpoint URL
            batch_id: Batch identifier
            error_message: Error description

        Returns:
            True if notification sent successfully, False otherwise
        """
        payload = self.build_batch_failed_payload(
            batch_id=batch_id,
            error_message=error_message,
        )

        return await self._send_webhook(callback_url, payload)

    def build_batch_progress_payload(
        self,
        batch_id: str,
        total_conversations: int,
        completed_count: int,
        failed_count: int,
        progress_percent: float,
    ) -> dict[str, Any]:
        """
        Build batch progress webhook payload.

        Args:
            batch_id: Batch identifier
            total_conversations: Total number of conversations
            completed_count: Number of completed analyses
            failed_count: Number of failed analyses
            progress_percent: Progress percentage

        Returns:
            Webhook payload dictionary
        """
        return {
            "event": "batch.progress",
            "timestamp": datetime.utcnow().isoformat(),
            "batch_id": batch_id,
            "data": {
                "total_conversations": total_conversations,
                "completed_count": completed_count,
                "failed_count": failed_count,
                "pending_count": total_conversations - completed_count - failed_count,
                "progress_percent": round(progress_percent, 2),
            },
        }

    def build_batch_complete_payload(
        self,
        batch_id: str,
        total_conversations: int,
        completed_count: int,
        failed_count: int,
    ) -> dict[str, Any]:
        """
        Build batch completion webhook payload.

        Args:
            batch_id: Batch identifier
            total_conversations: Total number of conversations
            completed_count: Number of successful analyses
            failed_count: Number of failed analyses

        Returns:
            Webhook payload dictionary
        """
        return {
            "event": "batch.complete",
            "timestamp": datetime.utcnow().isoformat(),
            "batch_id": batch_id,
            "data": {
                "total_conversations": total_conversations,
                "completed_count": completed_count,
                "failed_count": failed_count,
                "success_rate": round(completed_count / total_conversations * 100, 2) if total_conversations > 0 else 0.0,
            },
        }

    def build_batch_failed_payload(
        self,
        batch_id: str,
        error_message: str,
    ) -> dict[str, Any]:
        """
        Build batch failure webhook payload.

        Args:
            batch_id: Batch identifier
            error_message: Error description

        Returns:
            Webhook payload dictionary
        """
        return {
            "event": "batch.failed",
            "timestamp": datetime.utcnow().isoformat(),
            "batch_id": batch_id,
            "data": {
                "error": error_message,
            },
        }

    def generate_signature(self, payload: dict[str, Any], secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        This allows webhook consumers to verify that the webhook
        payload was sent by the Observatory service and hasn't been
        tampered with in transit.

        Args:
            payload: Webhook payload dictionary
            secret: Shared secret key for HMAC generation

        Returns:
            Hexadecimal signature string
        """
        # Convert payload to JSON with sorted keys for consistency
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        )

        return signature.hexdigest()

    async def _send_webhook(
        self,
        url: str,
        payload: dict[str, Any],
        timeout: Optional[float] = None,
        max_retries: int = 0,
    ) -> bool:
        """
        Send webhook HTTP POST request with retry support.

        Args:
            url: Webhook endpoint URL
            payload: JSON payload
            timeout: Request timeout in seconds (overrides default)
            max_retries: Maximum number of retry attempts on failure

        Returns:
            True if request succeeded (2xx status), False otherwise
        """
        # Use custom timeout or fall back to instance timeout
        request_timeout = timeout if timeout is not None else self.timeout

        # Try initial request + retries
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Atrium-Observatory/1.0",
                    },
                    timeout=request_timeout,
                )

                if response.status_code >= 200 and response.status_code < 300:
                    if attempt > 0:
                        logger.info(f"Webhook sent successfully to {url} on attempt {attempt + 1}: {payload['event']}")
                    else:
                        logger.info(f"Webhook sent successfully to {url}: {payload['event']}")
                    return True
                else:
                    logger.warning(
                        f"Webhook failed with status {response.status_code}: {url} (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    # Don't retry on client errors (4xx), only server errors (5xx)
                    if response.status_code < 500:
                        return False

            except httpx.TimeoutException as e:
                logger.error(f"Webhook timeout to {url}: {e} (attempt {attempt + 1}/{max_retries + 1})")
            except httpx.RequestError as e:
                logger.error(f"Webhook request error to {url}: {e} (attempt {attempt + 1}/{max_retries + 1})")
            except Exception as e:
                logger.error(f"Unexpected webhook error to {url}: {e} (attempt {attempt + 1}/{max_retries + 1})", exc_info=True)
                return False

        # All attempts failed
        logger.error(f"Webhook failed after {max_retries + 1} attempts to {url}")
        return False

    async def close(self):
        """Close HTTP client and cleanup resources."""
        await self.client.aclose()
