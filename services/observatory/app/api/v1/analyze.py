"""API endpoints for conversation analysis."""

from datetime import datetime, UTC
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatusResponse,
    CancelResponse,
)
from app.models.database import Analysis, AnalysisStatus, get_db_session
from app.core.analyzer import AnalyzerEngine
from app.core.validator import InputValidator
from app.core.jobs import JobManager
from app.core.config import settings
from app.core.export import ExportFormatter, ExportFormat
from app.core.logging import (
    log_analysis_created,
    log_analysis_completed,
    log_analysis_cancelled,
    log_analysis_failed,
)

router = APIRouter()

# Initialize core components
analyzer = AnalyzerEngine(
    ollama_base_url=settings.ollama_base_url,
    model=settings.ollama_model,
)
validator = InputValidator(max_length=settings.max_conversation_length)
job_manager = JobManager()


@router.post("/analyze", response_model=AnalysisStatusResponse, status_code=202)
async def create_analysis(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new conversation analysis request.
    
    Returns 202 Accepted with analysis ID and status.
    The analysis runs asynchronously in the background.
    """
    # Validate conversation text
    validation = validator.validate(request.conversation_text)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error)
    
    # Create database record
    analysis_id = str(uuid4())
    analysis = Analysis(
        id=analysis_id,
        conversation_text=request.conversation_text,
        status=AnalysisStatus.PENDING,
    )
    analysis.set_expiration()
    
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    # Log creation
    log_analysis_created(
        analysis_id=analysis_id,
        conversation_size=len(request.conversation_text),
        options=request.options.model_dump(),
    )
    
    # Start async analysis job
    async def run_analysis():
        """Background task to run analysis."""
        try:
            # Update status to processing
            analysis.status = AnalysisStatus.PROCESSING
            await db.commit()
            
            # Run analysis
            start_time = datetime.now(UTC).replace(tzinfo=None)
            result = await analyzer.analyze(
                conversation_text=request.conversation_text,
                pattern_types=request.options.pattern_types,
                include_insights=request.options.include_insights,
            )
            processing_time = (datetime.now(UTC).replace(tzinfo=None) - start_time).total_seconds()
            
            # Update database with results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.observer_output = result.get("observer_output")
            analysis.patterns = result.get("patterns")
            analysis.confidence_score = result.get("confidence_score")
            analysis.processing_time = processing_time
            await db.commit()
            
            # Log completion
            log_analysis_completed(
                analysis_id=analysis_id,
                status="completed",
                processing_time=processing_time,
                confidence_score=result.get("confidence_score"),
            )
            
        except Exception as e:
            # Update status to failed
            analysis.status = AnalysisStatus.FAILED
            analysis.error = str(e)
            analysis.processing_time = (datetime.now(UTC).replace(tzinfo=None) - start_time).total_seconds()
            await db.commit()
            
            # Log failure
            log_analysis_failed(
                analysis_id=analysis_id,
                error=str(e),
                processing_time=analysis.processing_time,
            )
    
    # Create background job
    await job_manager.create_job(
        run_analysis,
        timeout=settings.analysis_timeout,
    )
    
    # Return status response
    return AnalysisStatusResponse(
        id=analysis.id,
        status=analysis.status.value,
        created_at=analysis.created_at,
        expires_at=analysis.expires_at,
    )


@router.get("/analyze/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    format: Optional[str] = Query(None, description="Export format: json (default), csv, markdown"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve analysis results by ID.

    Returns full analysis details if completed,
    or status information if still processing.

    **Export Formats (FR-014)**:
    - `json` (default): JSON response
    - `csv`: Comma-separated values
    - `markdown` or `md`: Markdown formatted report
    """
    # Query database
    stmt = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found or expired")

    # Update last accessed timestamp
    analysis.update_last_accessed()
    await db.commit()

    # Build response data
    response_data = {
        "id": analysis.id,
        "status": analysis.status.value,
        "observer_output": analysis.observer_output,
        "patterns": analysis.patterns,
        "summary_points": None,  # TODO: Extract from observer_output
        "confidence_score": analysis.confidence_score,
        "processing_time": analysis.processing_time,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "expires_at": analysis.expires_at.isoformat() if analysis.expires_at else None,
        "error": analysis.error,
        "conversation_text": analysis.conversation_text,
    }

    # Handle export formats
    if format:
        try:
            export_format = ExportFormatter.detect_format(format)
            formatter = ExportFormatter()

            if export_format == ExportFormat.JSON:
                # Return pretty JSON for explicit format request
                content = formatter.to_json(response_data, pretty=True)
                return PlainTextResponse(content=content, media_type="application/json")
            elif export_format == ExportFormat.CSV:
                content = formatter.to_csv(response_data)
                return PlainTextResponse(content=content, media_type="text/csv")
            elif export_format == ExportFormat.MARKDOWN:
                content = formatter.to_markdown(response_data)
                return PlainTextResponse(content=content, media_type="text/markdown")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Default JSON response (Pydantic model)
    return AnalysisResponse(
        id=analysis.id,
        status=analysis.status.value,
        observer_output=analysis.observer_output,
        patterns=analysis.patterns,
        summary_points=None,
        confidence_score=analysis.confidence_score,
        processing_time=analysis.processing_time,
        created_at=analysis.created_at,
        expires_at=analysis.expires_at,
        error=analysis.error,
    )


@router.post("/analyze/{analysis_id}/cancel", response_model=CancelResponse)
async def cancel_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Cancel an ongoing analysis.
    
    Only pending or processing analyses can be cancelled.
    """
    # Query database
    stmt = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()
    
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Check if cancellable
    if analysis.status not in [AnalysisStatus.PENDING, AnalysisStatus.PROCESSING]:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot cancel analysis with status: {analysis.status.value}",
        )
    
    # Cancel the job (if still running)
    # Note: JobManager doesn't have job IDs tied to analysis IDs yet
    # This is a simplified implementation
    
    # Update status
    analysis.status = AnalysisStatus.CANCELLED
    await db.commit()
    
    # Log cancellation
    log_analysis_cancelled(analysis_id=analysis_id, initiated_by="user")
    
    return CancelResponse(
        id=analysis.id,
        status=analysis.status.value,
        message="Analysis cancelled successfully",
    )
