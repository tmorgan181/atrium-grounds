"""Structured audit logging for Observatory service."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


# Configure logging based on settings
def configure_logging() -> None:
    """Configure logging format and level."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        # JSON structured logging
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            handlers=[logging.StreamHandler()],
        )
    else:
        # Standard text logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )


# Get logger instance
logger = logging.getLogger("observatory")


def log_json(level: str, event: str, **kwargs: Any) -> None:
    """
    Log a structured JSON event.

    Args:
        level: Log level (info, warning, error, debug)
        event: Event type/name
        **kwargs: Additional fields to include in log
    """
    log_data = {
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        "event": event,
        **kwargs,
    }

    if settings.log_format == "json":
        log_message = json.dumps(log_data)
    else:
        # Format as readable text
        log_message = f"{event}: {', '.join(f'{k}={v}' for k, v in kwargs.items())}"

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(log_message)


# Analysis lifecycle events
def log_analysis_created(analysis_id: str, conversation_size: int, options: dict) -> None:
    """Log when a new analysis is created."""
    log_json(
        "info",
        "analysis_created",
        analysis_id=analysis_id,
        conversation_size=conversation_size,
        pattern_types=options.get("pattern_types", []),
        include_insights=options.get("include_insights", True),
    )


def log_analysis_completed(
    analysis_id: str,
    status: str,
    processing_time: float,
    confidence_score: float | None = None,
) -> None:
    """Log when an analysis completes."""
    log_json(
        "info",
        "analysis_completed",
        analysis_id=analysis_id,
        status=status,
        processing_time=processing_time,
        confidence_score=confidence_score,
    )


def log_analysis_cancelled(analysis_id: str, initiated_by: str = "user") -> None:
    """Log when an analysis is cancelled."""
    log_json(
        "info",
        "analysis_cancelled",
        analysis_id=analysis_id,
        initiated_by=initiated_by,
    )


def log_analysis_failed(analysis_id: str, error: str, processing_time: float) -> None:
    """Log when an analysis fails."""
    log_json(
        "error",
        "analysis_failed",
        analysis_id=analysis_id,
        error=error,
        processing_time=processing_time,
    )


# TTL cleanup events
def log_ttl_cleanup(
    deleted_results: int,
    old_metadata_count: int,
    oldest_deleted_date: str | None = None,
) -> None:
    """Log TTL cleanup execution."""
    log_json(
        "info",
        "ttl_cleanup",
        deleted_results=deleted_results,
        old_metadata_count=old_metadata_count,
        oldest_deleted_date=oldest_deleted_date,
    )


def log_ttl_cleanup_error(error: str) -> None:
    """Log TTL cleanup failure."""
    log_json(
        "error",
        "ttl_cleanup_error",
        error=error,
    )


# Rate limiting events
def log_rate_limit_exceeded(ip_address: str, tier: str, endpoint: str) -> None:
    """Log when rate limit is exceeded."""
    log_json(
        "warning",
        "rate_limit_exceeded",
        ip_address=ip_address,
        tier=tier,
        endpoint=endpoint,
    )


# Authentication events
def log_auth_success(api_key_prefix: str, tier: str) -> None:
    """Log successful authentication."""
    log_json(
        "info",
        "auth_success",
        api_key_prefix=api_key_prefix,
        tier=tier,
    )


def log_auth_failure(api_key_prefix: str, reason: str) -> None:
    """Log authentication failure."""
    log_json(
        "warning",
        "auth_failure",
        api_key_prefix=api_key_prefix,
        reason=reason,
    )


# Initialize logging on import
configure_logging()
