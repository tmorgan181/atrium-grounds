"""SQLAlchemy database models and connection management."""

import uuid
from datetime import datetime, timedelta
from typing import Optional, AsyncGenerator

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import enum
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
cleanup_scheduler = None


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

    # Ensure data directory exists for SQLite databases
    if "sqlite" in db_url:
        import os
        from pathlib import Path

        # Extract path from URL (e.g., "sqlite+aiosqlite:///./data/observatory.db")
        db_path = db_url.split("///")[-1]
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

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


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
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
    from sqlalchemy import select, delete
    from app.core.logging import log_ttl_cleanup, log_ttl_cleanup_error
    
    if async_session_maker is None:
        await init_database()

    try:
        async with async_session_maker() as session:
            now = datetime.utcnow()

            # Calculate cutoff dates
            results_cutoff = now - timedelta(days=settings.ttl_results)
            metadata_cutoff = now - timedelta(days=settings.ttl_metadata)

            # Find records to delete (based on last_accessed_at for results TTL)
            stmt = select(Analysis).where(Analysis.last_accessed_at < results_cutoff)
            result = await session.execute(stmt)
            to_delete = result.scalars().all()
            
            deleted_count = len(to_delete)
            oldest_date = min([r.last_accessed_at for r in to_delete], default=None)

            # Delete expired results
            if deleted_count > 0:
                delete_stmt = delete(Analysis).where(Analysis.last_accessed_at < results_cutoff)
                await session.execute(delete_stmt)
                await session.commit()

            # Count old metadata (90+ days old) - for future aggregation
            metadata_stmt = select(Analysis).where(Analysis.created_at < metadata_cutoff)
            metadata_result = await session.execute(metadata_stmt)
            old_metadata_count = len(metadata_result.scalars().all())

            # Log cleanup event
            log_ttl_cleanup(
                deleted_results=deleted_count,
                old_metadata_count=old_metadata_count,
                oldest_deleted_date=oldest_date.isoformat() if oldest_date else None,
            )

            return {
                "deleted_results": deleted_count,
                "old_metadata_count": old_metadata_count,
            }
    except Exception as e:
        log_ttl_cleanup_error(str(e))
        raise


def start_cleanup_scheduler() -> None:
    """Start the TTL cleanup scheduler."""
    global cleanup_scheduler
    
    if cleanup_scheduler is not None:
        return  # Already started
    
    cleanup_scheduler = AsyncIOScheduler()
    
    # Run cleanup daily at 2 AM
    cleanup_scheduler.add_job(
        cleanup_expired_records,
        CronTrigger(hour=2, minute=0),
        id="ttl_cleanup",
        name="TTL Cleanup Job",
        replace_existing=True,
    )
    
    cleanup_scheduler.start()


def stop_cleanup_scheduler() -> None:
    """Stop the TTL cleanup scheduler."""
    global cleanup_scheduler
    
    if cleanup_scheduler is not None:
        cleanup_scheduler.shutdown()
        cleanup_scheduler = None
