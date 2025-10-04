"""SQLAlchemy database models and connection management."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import enum

from app.core.config import settings


# SQLAlchemy Base
Base = declarative_base()


# Analysis Status Enum
class AnalysisStatus(str, enum.Enum):
    """Status values for analysis records."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Analysis(Base):
    """Database model for conversation analysis results."""

    __tablename__ = "analyses"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Conversation data
    conversation_text = Column(Text, nullable=False)

    # Analysis status
    status = Column(SQLEnum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)

    # Analysis results
    observer_output = Column(Text, nullable=True)
    patterns = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)

    # Error information
    error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """String representation of Analysis model."""
        return f"<Analysis(id={self.id}, status={self.status}, created_at={self.created_at})>"

    def set_expiration(self) -> None:
        """Set expiration date based on TTL configuration."""
        self.expires_at = datetime.utcnow() + timedelta(days=settings.ttl_results)

    def update_last_accessed(self) -> None:
        """Update last_accessed_at timestamp."""
        self.last_accessed_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if analysis result has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


# Database engine and session management
engine = None
async_session_maker = None


def get_database_url() -> str:
    """Get the appropriate async database URL."""
    db_url = settings.database_url

    # Convert sync SQLite URL to async
    if db_url.startswith("sqlite:///"):
        db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    # PostgreSQL async support
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    return db_url


async def init_database() -> None:
    """Initialize database connection and create tables."""
    global engine, async_session_maker

    db_url = get_database_url()

    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=settings.log_level == "DEBUG",
        pool_pre_ping=True,
    )

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncSession:
    """Get an async database session."""
    if async_session_maker is None:
        await init_database()

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def cleanup_expired_records() -> dict[str, int]:
    """
    Clean up expired analysis records based on TTL configuration.
    
    Returns:
        Dictionary with counts of deleted results and metadata.
    """
    if async_session_maker is None:
        await init_database()

    async with async_session_maker() as session:
        now = datetime.utcnow()

        # Calculate cutoff dates
        results_cutoff = now - timedelta(days=settings.ttl_results)
        metadata_cutoff = now - timedelta(days=settings.ttl_metadata)

        # Delete results older than TTL (based on last_accessed_at)
        results_query = await session.execute(
            """
            DELETE FROM analyses
            WHERE last_accessed_at < :cutoff
            RETURNING id
            """,
            {"cutoff": results_cutoff}
        )
        deleted_results = len(results_query.fetchall())

        # For metadata cleanup, we'd delete the entire record
        # but keep aggregated insights (Phase 5 enhancement)
        # For now, just track metadata older than 90 days
        metadata_query = await session.execute(
            """
            SELECT COUNT(*) FROM analyses
            WHERE created_at < :cutoff
            """,
            {"cutoff": metadata_cutoff}
        )
        old_metadata_count = metadata_query.scalar()

        await session.commit()

        return {
            "deleted_results": deleted_results,
            "old_metadata_count": old_metadata_count,
        }
