"""Job management system for cancellable async analysis tasks."""

import asyncio
import uuid
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, ConfigDict


class JobStatus(str, Enum):
    """Status of a job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(BaseModel):
    """Represents an analysis job."""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class JobManager:
    """
    Manages async analysis jobs with cancellation support.

    Based on ProcessManager from original Observatory:
    - Job creation and tracking
    - Cancellable async tasks
    - Status monitoring
    - Result retrieval
    - Timeout handling
    """

    def __init__(self):
        """Initialize job manager."""
        self.jobs: dict[str, Job] = {}
        self.tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def create_job(
        self, task_func: Callable, *args, timeout: Optional[float] = None, **kwargs
    ) -> str:
        """
        Create and start a new job.

        Args:
            task_func: Async function to execute
            *args: Positional arguments for task_func
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for task_func

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        # Create job record (using naive UTC datetime)
        job = Job(
            id=job_id, status=JobStatus.PENDING, created_at=datetime.now(UTC).replace(tzinfo=None)
        )

        async with self._lock:
            self.jobs[job_id] = job

        # Create and start task
        task = asyncio.create_task(self._run_job(job_id, task_func, timeout, *args, **kwargs))

        async with self._lock:
            self.tasks[job_id] = task
            self.jobs[job_id].status = JobStatus.RUNNING

        return job_id

    async def _run_job(
        self,
        job_id: str,
        task_func: Callable,
        timeout: Optional[float],
        *args,
        **kwargs,
    ):
        """
        Internal method to run a job with timeout and error handling.

        Args:
            job_id: Job identifier
            task_func: Function to execute
            timeout: Optional timeout in seconds
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        try:
            # Run with timeout if specified
            if timeout:
                result = await asyncio.wait_for(task_func(*args, **kwargs), timeout=timeout)
            else:
                result = await task_func(*args, **kwargs)

            # Mark as completed
            async with self._lock:
                if self.jobs[job_id].status != JobStatus.CANCELLED:
                    self.jobs[job_id].status = JobStatus.COMPLETED
                    self.jobs[job_id].result = result
                    self.jobs[job_id].completed_at = datetime.now(UTC).replace(tzinfo=None)

        except asyncio.CancelledError:
            # Job was cancelled
            async with self._lock:
                self.jobs[job_id].status = JobStatus.CANCELLED
                self.jobs[job_id].completed_at = datetime.now(UTC).replace(tzinfo=None)

        except asyncio.TimeoutError:
            # Job timed out
            async with self._lock:
                self.jobs[job_id].status = JobStatus.FAILED
                self.jobs[job_id].error = f"Job timed out after {timeout} seconds"
                self.jobs[job_id].completed_at = datetime.now(UTC).replace(tzinfo=None)

        except Exception as e:
            # Job failed with error
            async with self._lock:
                self.jobs[job_id].status = JobStatus.FAILED
                self.jobs[job_id].error = str(e)
                self.jobs[job_id].completed_at = datetime.now(UTC).replace(tzinfo=None)

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.

        Args:
            job_id: Job identifier

        Returns:
            True if job was cancelled, False if job doesn't exist or already completed
        """
        async with self._lock:
            if job_id not in self.jobs:
                return False

            job = self.jobs[job_id]

            # Can only cancel pending or running jobs
            if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
                return False

            # Cancel the task
            if job_id in self.tasks:
                self.tasks[job_id].cancel()

            # Update status
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(UTC).replace(tzinfo=None)

        return True

    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Get the status of a job.

        Args:
            job_id: Job identifier

        Returns:
            JobStatus or None if job doesn't exist
        """
        async with self._lock:
            if job_id not in self.jobs:
                return None
            return self.jobs[job_id].status

    async def get_job_result(self, job_id: str) -> Optional[dict[str, Any]]:
        """
        Get the result of a completed job.

        Args:
            job_id: Job identifier

        Returns:
            Job result or None if job doesn't exist or isn't completed
        """
        async with self._lock:
            if job_id not in self.jobs:
                return None

            job = self.jobs[job_id]

            if job.status != JobStatus.COMPLETED:
                return None

            return job.result

    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get full job information.

        Args:
            job_id: Job identifier

        Returns:
            Job object or None if not found
        """
        async with self._lock:
            return self.jobs.get(job_id)

    async def shutdown(self):
        """Cancel all running jobs and cleanup."""
        async with self._lock:
            for task in self.tasks.values():
                if not task.done():
                    task.cancel()

            # Wait for all tasks to complete
            if self.tasks:
                await asyncio.gather(*self.tasks.values(), return_exceptions=True)

            self.tasks.clear()
