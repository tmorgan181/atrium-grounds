"""Tests for database models and operations."""

import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.database import Base, Analysis, AnalysisStatus, get_database_url


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

    async with async_session() as session:
        yield session

    # Clean up
    await engine.dispose()


@pytest.mark.asyncio
async def test_analysis_model_creation(test_db_session):
    """Test creating an Analysis record."""
    analysis = Analysis(
        conversation_text="Test conversation",
        status=AnalysisStatus.PENDING,
    )

    test_db_session.add(analysis)
    await test_db_session.commit()

    assert analysis.id is not None
    assert analysis.status == AnalysisStatus.PENDING
    assert analysis.conversation_text == "Test conversation"
    assert analysis.created_at is not None
    assert analysis.last_accessed_at is not None


@pytest.mark.asyncio
async def test_analysis_set_expiration(test_db_session):
    """Test setting expiration date."""
    analysis = Analysis(conversation_text="Test")
    analysis.set_expiration()

    assert analysis.expires_at is not None
    # Should expire 30 days from now (default TTL)
    expected_expiry = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=30)
    # Allow 1 second tolerance
    assert abs((analysis.expires_at - expected_expiry).total_seconds()) < 1


@pytest.mark.asyncio
async def test_analysis_is_expired(test_db_session):
    """Test expiration check."""
    # Not expired
    analysis_fresh = Analysis(conversation_text="Test")
    analysis_fresh.expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    assert not analysis_fresh.is_expired()

    # Expired
    analysis_old = Analysis(conversation_text="Test")
    analysis_old.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1)
    assert analysis_old.is_expired()

    # No expiration set
    analysis_no_expiry = Analysis(conversation_text="Test")
    assert not analysis_no_expiry.is_expired()


@pytest.mark.asyncio
async def test_analysis_update_last_accessed(test_db_session):
    """Test updating last accessed timestamp."""
    analysis = Analysis(conversation_text="Test")
    
    # Manually set initial timestamp since default only applies on DB insert
    analysis.last_accessed_at = datetime.now(UTC).replace(tzinfo=None)
    original_time = analysis.last_accessed_at

    # Wait a moment and update
    import asyncio
    await asyncio.sleep(0.01)

    analysis.update_last_accessed()
    assert analysis.last_accessed_at > original_time


@pytest.mark.asyncio
async def test_analysis_status_enum():
    """Test all status values are valid."""
    assert AnalysisStatus.PENDING.value == "pending"
    assert AnalysisStatus.PROCESSING.value == "processing"
    assert AnalysisStatus.COMPLETED.value == "completed"
    assert AnalysisStatus.FAILED.value == "failed"
    assert AnalysisStatus.CANCELLED.value == "cancelled"


@pytest.mark.asyncio
async def test_get_database_url_sqlite():
    """Test SQLite URL conversion to async."""
    from app.core.config import settings

    # Store original
    original = settings.database_url

    # Test SQLite conversion
    settings.database_url = "sqlite:///./test.db"
    url = get_database_url()
    assert url == "sqlite+aiosqlite:///./test.db"

    # Restore
    settings.database_url = original


@pytest.mark.asyncio
async def test_get_database_url_postgresql():
    """Test PostgreSQL URL conversion to async."""
    from app.core.config import settings

    # Store original
    original = settings.database_url

    # Test PostgreSQL conversion
    settings.database_url = "postgresql://user:pass@localhost/db"
    url = get_database_url()
    assert url == "postgresql+asyncpg://user:pass@localhost/db"

    # Restore
    settings.database_url = original
