"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalysisOptions(BaseModel):
    """Options for conversation analysis."""

    pattern_types: list[str] = Field(
        default=["dialectic", "sentiment", "topics", "dynamics"],
        description="Types of patterns to detect",
    )
    include_insights: bool = Field(default=True, description="Include natural language insights")
    callback_url: str | None = Field(
        default=None, description="Webhook URL for async notifications"
    )


class AnalysisRequest(BaseModel):
    """Request to analyze a conversation."""

    conversation_text: str = Field(..., description="Raw conversation transcript")
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class PatternData(BaseModel):
    """Detected pattern data."""

    dialectic: list[dict[str, Any]] = Field(default_factory=list)
    sentiment: dict[str, Any] = Field(default_factory=dict)
    topics: list[str] = Field(default_factory=list)
    dynamics: dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Response containing analysis results."""

    id: str = Field(..., description="Unique analysis identifier")
    status: str = Field(
        ..., description="Analysis status: pending, processing, completed, failed, cancelled"
    )
    observer_output: str | None = Field(
        default=None, description="Natural language analysis from Observer model"
    )
    patterns: PatternData | None = Field(default=None, description="Detected patterns")
    summary_points: list[str] | None = Field(default=None, description="Key insights summary")
    confidence_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    processing_time: float | None = Field(default=None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Timestamp when analysis was created")
    expires_at: datetime | None = Field(default=None, description="Timestamp when results expire")
    error: str | None = Field(default=None, description="Error message if analysis failed")


class AnalysisStatusResponse(BaseModel):
    """Minimal response for status checks."""

    id: str
    status: str
    created_at: datetime
    expires_at: datetime | None = None


class CancelResponse(BaseModel):
    """Response for cancellation request."""

    id: str
    status: str
    message: str = "Analysis cancelled successfully"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    timestamp: datetime
    version: str
