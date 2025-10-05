"""Tests for TTL enforcement and cleanup."""

import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.database import Base, Analysis, AnalysisStatus, cleanup_expired_records
from app.core.config import settings


@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Temporarily override the global session maker for cleanup function
    import app.models.database as db_module
    original_session_maker = db_module.async_session_maker
    db_module.async_session_maker = async_session

    async with async_session() as session:
        yield session

    # Restore original session maker
    db_module.async_session_maker = original_session_maker

    # Clean up
    await engine.dispose()


@pytest.mark.asyncio
async def test_ttl_30_day_results_expiration(test_db_session):
    """Test that results older than 30 days are deleted."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Create fresh analysis (should NOT be deleted)
    fresh_analysis = Analysis(
        conversation_text="Fresh conversation",
        status=AnalysisStatus.COMPLETED,
        last_accessed_at=now - timedelta(days=15),
    )
    test_db_session.add(fresh_analysis)
    
    # Create old analysis (should be deleted)
    old_analysis = Analysis(
        conversation_text="Old conversation",
        status=AnalysisStatus.COMPLETED,
        last_accessed_at=now - timedelta(days=31),
    )
    test_db_session.add(old_analysis)
    
    # Create very old analysis (should be deleted)
    very_old_analysis = Analysis(
        conversation_text="Very old conversation",
        status=AnalysisStatus.COMPLETED,
        last_accessed_at=now - timedelta(days=60),
    )
    test_db_session.add(very_old_analysis)
    
    await test_db_session.commit()
    
    # Run cleanup
    result = await cleanup_expired_records()
    
    # Should delete 2 old records
    assert result["deleted_results"] == 2
    
    # Verify fresh record still exists
    await test_db_session.refresh(fresh_analysis)
    assert fresh_analysis.id is not None


@pytest.mark.asyncio
async def test_ttl_90_day_metadata_tracking(test_db_session):
    """Test that metadata older than 90 days is tracked."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Create analysis with old metadata (created 91 days ago)
    old_metadata = Analysis(
        conversation_text="Old metadata",
        status=AnalysisStatus.COMPLETED,
        created_at=now - timedelta(days=91),
        last_accessed_at=now - timedelta(days=1),  # Recently accessed, so not deleted yet
    )
    test_db_session.add(old_metadata)
    
    # Create analysis with recent metadata
    recent_metadata = Analysis(
        conversation_text="Recent metadata",
        status=AnalysisStatus.COMPLETED,
        created_at=now - timedelta(days=30),
        last_accessed_at=now - timedelta(days=1),
    )
    test_db_session.add(recent_metadata)
    
    await test_db_session.commit()
    
    # Run cleanup
    result = await cleanup_expired_records()
    
    # Should track 1 record with old metadata
    assert result["old_metadata_count"] == 1
    
    # Neither should be deleted (both accessed recently)
    assert result["deleted_results"] == 0


@pytest.mark.asyncio
async def test_ttl_cleanup_preserves_recent_records(test_db_session):
    """Test that recently accessed records are preserved."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Create multiple recent analyses
    for i in range(5):
        analysis = Analysis(
            conversation_text=f"Recent conversation {i}",
            status=AnalysisStatus.COMPLETED,
            last_accessed_at=now - timedelta(days=i),  # 0-4 days old
        )
        test_db_session.add(analysis)
    
    await test_db_session.commit()
    
    # Run cleanup
    result = await cleanup_expired_records()
    
    # Nothing should be deleted
    assert result["deleted_results"] == 0


@pytest.mark.asyncio
async def test_ttl_cleanup_handles_empty_database(test_db_session):
    """Test cleanup with no records."""
    result = await cleanup_expired_records()
    
    assert result["deleted_results"] == 0
    assert result["old_metadata_count"] == 0


@pytest.mark.asyncio
async def test_ttl_cleanup_handles_mixed_statuses(test_db_session):
    """Test cleanup with different analysis statuses."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Old completed analysis (should be deleted)
    old_completed = Analysis(
        conversation_text="Old completed",
        status=AnalysisStatus.COMPLETED,
        last_accessed_at=now - timedelta(days=31),
    )
    test_db_session.add(old_completed)
    
    # Old failed analysis (should be deleted)
    old_failed = Analysis(
        conversation_text="Old failed",
        status=AnalysisStatus.FAILED,
        last_accessed_at=now - timedelta(days=31),
    )
    test_db_session.add(old_failed)
    
    # Old pending analysis (should be deleted - stuck job)
    old_pending = Analysis(
        conversation_text="Old pending",
        status=AnalysisStatus.PENDING,
        last_accessed_at=now - timedelta(days=31),
    )
    test_db_session.add(old_pending)
    
    await test_db_session.commit()
    
    # Run cleanup
    result = await cleanup_expired_records()
    
    # All old records should be deleted regardless of status
    assert result["deleted_results"] == 3


@pytest.mark.asyncio
async def test_ttl_expiration_with_custom_settings(test_db_session):
    """Test TTL with different configuration values."""
    # Store original settings
    original_ttl_results = settings.ttl_results
    original_ttl_metadata = settings.ttl_metadata
    
    try:
        # Set custom TTL (shorter for testing)
        settings.ttl_results = 7  # 7 days instead of 30
        settings.ttl_metadata = 14  # 14 days instead of 90
        
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Create analysis older than custom TTL
        old_analysis = Analysis(
            conversation_text="Old with custom TTL",
            status=AnalysisStatus.COMPLETED,
            last_accessed_at=now - timedelta(days=8),  # 8 > 7 days
        )
        test_db_session.add(old_analysis)
        
        await test_db_session.commit()
        
        # Run cleanup with custom settings
        result = await cleanup_expired_records()
        
        # Should delete the old record based on custom TTL
        assert result["deleted_results"] == 1
        
    finally:
        # Restore original settings
        settings.ttl_results = original_ttl_results
        settings.ttl_metadata = original_ttl_metadata
