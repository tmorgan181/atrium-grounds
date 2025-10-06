"""Health check and metrics endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.middleware.auth import get_current_tier
from app.models.database import Analysis, get_db_session
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns service status, version, and timestamp.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(UTC).replace(tzinfo=None),
    )


@router.get("/metrics")
async def get_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get usage metrics for authenticated users.

    Requires API key or higher authentication.
    Returns request counts, rate limit status, and database statistics.
    """
    # Check authentication
    tier = get_current_tier(request)
    if tier == "public":
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide API key via Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get database statistics
    total_analyses = await db.scalar(select(func.count(Analysis.id)))

    completed_analyses = await db.scalar(
        select(func.count(Analysis.id)).where(Analysis.status == "completed")
    )

    avg_processing_time = await db.scalar(
        select(func.avg(Analysis.processing_time)).where(Analysis.processing_time.isnot(None))
    )

    # Get rate limit info from request state
    from app.middleware.ratelimit import TierLimits

    tier_limits = TierLimits.get_limits(tier)

    return {
        "tier": tier,
        "rate_limits": {
            "requests_per_minute": tier_limits["requests_per_minute"],
            "requests_per_day": tier_limits["requests_per_day"],
        },
        "database_stats": {
            "total_analyses": total_analyses or 0,
            "completed_analyses": completed_analyses or 0,
            "avg_processing_time": float(avg_processing_time) if avg_processing_time else 0.0,
        },
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
    }
