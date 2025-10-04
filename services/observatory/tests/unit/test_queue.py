"""Unit tests for Redis job queue management."""

import pytest
import asyncio
from app.core.queue import JobQueue, BatchJob, JobPriority


@pytest.fixture
async def job_queue():
    """Create job queue instance."""
    queue = JobQueue()
    yield queue
    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_initialization(job_queue):
    """Test that queue initializes correctly."""
    assert job_queue is not None
    assert hasattr(job_queue, "enqueue")
    assert hasattr(job_queue, "dequeue")


@pytest.mark.asyncio
async def test_enqueue_batch_job():
    """Test enqueueing a batch job."""
    queue = JobQueue()

    batch_job = BatchJob(
        batch_id="batch-123",
        conversation_ids=["conv-1", "conv-2", "conv-3"],
        options={"pattern_types": ["dialectic"]},
    )

    job_id = await queue.enqueue(batch_job)

    assert job_id is not None
    assert isinstance(job_id, str)

    await queue.shutdown()


@pytest.mark.asyncio
async def test_dequeue_job():
    """Test dequeueing a job from queue."""
    queue = JobQueue()

    # Enqueue a job
    batch_job = BatchJob(
        batch_id="batch-123",
        conversation_ids=["conv-1"],
        options={},
    )
    await queue.enqueue(batch_job)

    # Dequeue it
    dequeued = await queue.dequeue()

    assert dequeued is not None
    assert dequeued.batch_id == "batch-123"

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_fifo_order():
    """Test jobs are dequeued in FIFO order."""
    queue = JobQueue()

    # Enqueue multiple jobs
    job1 = BatchJob(batch_id="batch-1", conversation_ids=["conv-1"], options={})
    job2 = BatchJob(batch_id="batch-2", conversation_ids=["conv-2"], options={})
    job3 = BatchJob(batch_id="batch-3", conversation_ids=["conv-3"], options={})

    await queue.enqueue(job1)
    await queue.enqueue(job2)
    await queue.enqueue(job3)

    # Dequeue in order
    first = await queue.dequeue()
    second = await queue.dequeue()
    third = await queue.dequeue()

    assert first.batch_id == "batch-1"
    assert second.batch_id == "batch-2"
    assert third.batch_id == "batch-3"

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_priority():
    """Test priority queue functionality."""
    queue = JobQueue()

    # Enqueue with different priorities
    low_job = BatchJob(
        batch_id="batch-low",
        conversation_ids=["conv-1"],
        options={},
        priority=JobPriority.LOW,
    )
    high_job = BatchJob(
        batch_id="batch-high",
        conversation_ids=["conv-2"],
        options={},
        priority=JobPriority.HIGH,
    )
    normal_job = BatchJob(
        batch_id="batch-normal",
        conversation_ids=["conv-3"],
        options={},
        priority=JobPriority.NORMAL,
    )

    # Enqueue in low, high, normal order
    await queue.enqueue(low_job)
    await queue.enqueue(high_job)
    await queue.enqueue(normal_job)

    # High priority should come first
    first = await queue.dequeue()
    assert first.batch_id == "batch-high"

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_empty():
    """Test dequeueing from empty queue."""
    queue = JobQueue()

    # Should return None or wait (depending on implementation)
    dequeued = await asyncio.wait_for(queue.dequeue(), timeout=0.5)

    assert dequeued is None

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_size():
    """Test getting queue size."""
    queue = JobQueue()

    # Initially empty
    assert await queue.size() == 0

    # Add jobs
    await queue.enqueue(BatchJob(batch_id="batch-1", conversation_ids=["conv-1"], options={}))
    await queue.enqueue(BatchJob(batch_id="batch-2", conversation_ids=["conv-2"], options={}))

    assert await queue.size() == 2

    # Dequeue one
    await queue.dequeue()
    assert await queue.size() == 1

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_cancel_job():
    """Test cancelling a queued job."""
    queue = JobQueue()

    batch_job = BatchJob(batch_id="batch-123", conversation_ids=["conv-1"], options={})
    job_id = await queue.enqueue(batch_job)

    # Cancel it
    result = await queue.cancel(job_id)
    assert result is True

    # Should not be dequeued
    size = await queue.size()
    assert size == 0

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_get_status():
    """Test getting queue status/statistics."""
    queue = JobQueue()

    # Add some jobs
    await queue.enqueue(BatchJob(batch_id="batch-1", conversation_ids=["conv-1"], options={}))
    await queue.enqueue(BatchJob(batch_id="batch-2", conversation_ids=["conv-2"], options={}))

    status = await queue.get_status()

    assert "pending_jobs" in status
    assert status["pending_jobs"] == 2

    await queue.shutdown()


@pytest.mark.asyncio
async def test_queue_persistence():
    """Test that queue persists jobs in Redis."""
    queue1 = JobQueue()

    # Enqueue a job
    batch_job = BatchJob(batch_id="batch-persistent", conversation_ids=["conv-1"], options={})
    await queue1.enqueue(batch_job)
    await queue1.shutdown()

    # Create new queue instance
    queue2 = JobQueue()

    # Job should still be there
    size = await queue2.size()
    assert size == 1

    dequeued = await queue2.dequeue()
    assert dequeued.batch_id == "batch-persistent"

    await queue2.shutdown()
