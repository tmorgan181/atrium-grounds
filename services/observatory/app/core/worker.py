"""Async worker process for batch analysis."""

import asyncio
import logging
from typing import Optional

from app.core.analyzer import AnalyzerEngine
from app.core.validator import InputValidator
from app.core.queue import JobQueue, BatchJob
from app.core.notifications import WebhookNotifier
from app.core.config import settings

logger = logging.getLogger(__name__)


class BatchWorker:
    """
    Async worker that processes batch analysis jobs from Redis queue.

    Features:
    - Pulls jobs from queue
    - Validates and analyzes conversations
    - Tracks progress and failures
    - Sends webhook notifications
    - Handles cancellation
    """

    def __init__(
        self,
        queue: Optional[JobQueue] = None,
        analyzer: Optional[AnalyzerEngine] = None,
        validator: Optional[InputValidator] = None,
        notifier: Optional[WebhookNotifier] = None,
    ):
        """Initialize worker with dependencies."""
        self.queue = queue or JobQueue()
        self.analyzer = analyzer or AnalyzerEngine(
            ollama_base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
        self.validator = validator or InputValidator(max_length=settings.max_conversation_length)
        self.notifier = notifier or WebhookNotifier()
        self.running = False
        self.current_job: Optional[BatchJob] = None

    async def start(self):
        """Start the worker loop."""
        self.running = True
        logger.info("Batch worker started")

        while self.running:
            try:
                # Dequeue next job (blocks for 5 seconds)
                job = await self.queue.dequeue(timeout=5)

                if job:
                    self.current_job = job
                    await self.process_job(job)
                    self.current_job = None

            except asyncio.CancelledError:
                logger.info("Worker received cancellation signal")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Brief pause before retry

        logger.info("Batch worker stopped")

    async def stop(self):
        """Stop the worker loop."""
        self.running = False

    async def process_job(self, job: BatchJob):
        """
        Process a batch analysis job.

        Args:
            job: BatchJob to process
        """
        logger.info(f"Processing batch {job.batch_id} with {len(job.conversation_ids)} conversations")

        total_conversations = len(job.conversation_ids)
        completed_count = 0
        failed_count = 0
        results = {}

        try:
            for conv_id in job.conversation_ids:
                try:
                    # In real implementation, would fetch conversation text
                    # For now, assume conversation_ids contain the text
                    conversation_text = conv_id

                    # Validate
                    validation = self.validator.validate(conversation_text)
                    if not validation.is_valid:
                        logger.warning(
                            f"Batch {job.batch_id}: Conversation {conv_id} validation failed: {validation.error}"
                        )
                        failed_count += 1
                        results[conv_id] = {"status": "failed", "error": validation.error}
                        continue

                    # Analyze
                    analysis_result = await self.analyzer.analyze(validation.sanitized_text)

                    completed_count += 1
                    results[conv_id] = {
                        "status": "completed",
                        "patterns": analysis_result["patterns"],
                        "confidence_score": analysis_result["confidence_score"],
                    }

                    # Progress update (every 10%)
                    progress = (completed_count + failed_count) / total_conversations * 100
                    if progress % 10 < (1 / total_conversations * 100):
                        if callback_url := job.options.get("callback_url"):
                            await self.notifier.send_batch_progress(
                                callback_url=callback_url,
                                batch_id=job.batch_id,
                                total_conversations=total_conversations,
                                completed_count=completed_count,
                                failed_count=failed_count,
                                progress_percent=progress,
                            )

                except Exception as e:
                    logger.error(f"Batch {job.batch_id}: Failed to analyze {conv_id}: {e}")
                    failed_count += 1
                    results[conv_id] = {"status": "failed", "error": str(e)}

            # Send completion webhook
            if callback_url := job.options.get("callback_url"):
                await self.notifier.send_batch_complete(
                    callback_url=callback_url,
                    batch_id=job.batch_id,
                    total_conversations=total_conversations,
                    completed_count=completed_count,
                    failed_count=failed_count,
                )

            logger.info(
                f"Batch {job.batch_id} complete: {completed_count} succeeded, {failed_count} failed"
            )

        except Exception as e:
            logger.error(f"Batch {job.batch_id} failed: {e}", exc_info=True)

            # Send failure webhook
            if callback_url := job.options.get("callback_url"):
                await self.notifier.send_batch_failed(
                    callback_url=callback_url,
                    batch_id=job.batch_id,
                    error_message=str(e),
                )

    async def shutdown(self):
        """Shutdown worker and cleanup resources."""
        await self.stop()
        await self.analyzer.close()
        await self.notifier.close()
        await self.queue.shutdown()


async def run_worker():
    """Entry point for running the batch worker."""
    worker = BatchWorker()

    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    finally:
        await worker.shutdown()


if __name__ == "__main__":
    # Can run worker standalone
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
