"""Redis-based job queue for batch processing."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel, ConfigDict

from app.core.config import settings


class JobPriority(int, Enum):
    """Priority levels for job queue."""

    LOW = 0
    NORMAL = 1
    HIGH = 2


class BatchJob(BaseModel):
    """Represents a batch analysis job."""

    model_config = ConfigDict(use_enum_values=True)

    batch_id: str
    conversation_ids: list[str]
    options: dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    created_at: datetime = None

    def __init__(self, **data):
        if "created_at" not in data:
            data["created_at"] = datetime.now(UTC).replace(tzinfo=None)
        super().__init__(**data)


class JobQueue:
    """
    Redis-based job queue for batch processing.

    Features:
    - FIFO queue with priority support
    - Persistent storage in Redis
    - Job cancellation
    - Queue statistics
    """

    def __init__(self, redis_url: str = None):
        """Initialize job queue with Redis connection."""
        self.redis_url = redis_url or settings.redis_url
        self.redis_client: redis.Redis | None = None
        self.queue_key = "observatory:job_queue"
        self.priority_queue_key = "observatory:priority_queue"
        self.job_data_prefix = "observatory:job:"

    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url, decode_responses=True, encoding="utf-8"
            )

    async def enqueue(self, job: BatchJob) -> str:
        """
        Add a job to the queue.

        Args:
            job: BatchJob to enqueue

        Returns:
            Job ID
        """
        await self._ensure_connection()

        job_id = str(uuid.uuid4())

        # Store job data
        job_data_key = f"{self.job_data_prefix}{job_id}"
        await self.redis_client.set(job_data_key, job.model_dump_json())

        # Add to appropriate queue based on priority
        if job.priority == JobPriority.HIGH:
            await self.redis_client.rpush(self.priority_queue_key, job_id)
        else:
            await self.redis_client.rpush(self.queue_key, job_id)

        return job_id

    async def dequeue(self, timeout: float = 0) -> BatchJob | None:
        """
        Remove and return a job from the queue.

        Args:
            timeout: Seconds to wait for a job (0 = return immediately if empty)

        Returns:
            BatchJob or None if queue is empty
        """
        await self._ensure_connection()

        # Check priority queue first
        job_id = await self.redis_client.lpop(self.priority_queue_key)

        # If no priority jobs, check normal queue
        if not job_id:
            if timeout > 0:
                result = await self.redis_client.blpop(self.queue_key, timeout=int(timeout))
                job_id = result[1] if result else None
            else:
                job_id = await self.redis_client.lpop(self.queue_key)

        if not job_id:
            return None

        # Retrieve job data
        job_data_key = f"{self.job_data_prefix}{job_id}"
        job_json = await self.redis_client.get(job_data_key)

        if not job_json:
            return None

        # Delete job data after retrieval
        await self.redis_client.delete(job_data_key)

        return BatchJob.model_validate_json(job_json)

    async def cancel(self, job_id: str) -> bool:
        """
        Cancel a queued job.

        Args:
            job_id: Job identifier

        Returns:
            True if job was cancelled, False if not found
        """
        await self._ensure_connection()

        # Remove from both queues
        removed_normal = await self.redis_client.lrem(self.queue_key, 1, job_id)
        removed_priority = await self.redis_client.lrem(self.priority_queue_key, 1, job_id)

        if removed_normal or removed_priority:
            # Delete job data
            job_data_key = f"{self.job_data_prefix}{job_id}"
            await self.redis_client.delete(job_data_key)
            return True

        return False

    async def size(self) -> int:
        """
        Get total number of jobs in queue.

        Returns:
            Number of pending jobs
        """
        await self._ensure_connection()

        normal_size = await self.redis_client.llen(self.queue_key)
        priority_size = await self.redis_client.llen(self.priority_queue_key)

        return normal_size + priority_size

    async def get_status(self) -> dict[str, Any]:
        """
        Get queue status and statistics.

        Returns:
            Dictionary with queue metrics
        """
        await self._ensure_connection()

        normal_size = await self.redis_client.llen(self.queue_key)
        priority_size = await self.redis_client.llen(self.priority_queue_key)

        return {
            "pending_jobs": normal_size + priority_size,
            "normal_queue_size": normal_size,
            "priority_queue_size": priority_size,
        }

    async def clear(self):
        """Clear all jobs from queue (for testing)."""
        await self._ensure_connection()

        await self.redis_client.delete(self.queue_key)
        await self.redis_client.delete(self.priority_queue_key)

        # Clear all job data
        pattern = f"{self.job_data_prefix}*"
        cursor = 0
        while True:
            cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                await self.redis_client.delete(*keys)
            if cursor == 0:
                break

    async def shutdown(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
