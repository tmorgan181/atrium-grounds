"""
Observatory API proxy.

Proxies requests to Observatory service with authentication and error handling.
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from app.client import ObservatoryClient, get_observatory_client
import httpx

router = APIRouter(prefix="/api")


class AnalyzeRequest(BaseModel):
    """Request body for analyze endpoint."""

    conversation: list[dict[str, str]]


@router.post("/analyze")
async def analyze_conversation(
    request: AnalyzeRequest,
    x_api_key: str | None = Header(None),
    client: ObservatoryClient = Depends(get_observatory_client),
):
    """
    Proxy conversation analysis to Observatory.

    Requires API key authentication. Forwards request to Observatory
    and returns analysis results.

    Args:
        request: Conversation to analyze
        x_api_key: Observatory API key (header)
        client: Observatory HTTP client

    Returns:
        Analysis result from Observatory (patterns, sentiment, topics)

    Raises:
        HTTPException 401: Missing or invalid API key
        HTTPException 400: Invalid request
        HTTPException 503: Observatory service unavailable
    """
    # Require API key for custom analysis
    if not x_api_key:
        raise HTTPException(
            status_code=401, detail="API key required. Include X-API-Key header."
        )

    try:
        # Forward to Observatory
        result = await client.analyze(
            conversation=request.conversation, api_key=x_api_key
        )
        return result

    except httpx.HTTPStatusError as e:
        # Observatory returned error status
        if e.response.status_code == 401 or e.response.status_code == 403:
            raise HTTPException(status_code=401, detail="Invalid API key")
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers=dict(e.response.headers),
            )
        elif e.response.status_code == 400:
            raise HTTPException(
                status_code=400, detail=f"Invalid request: {e.response.text}"
            )
        else:
            raise HTTPException(status_code=503, detail="Observatory service error")

    except httpx.RequestError as e:
        # Connection error
        raise HTTPException(
            status_code=503, detail=f"Unable to reach Observatory service: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
async def observatory_health(
    client: ObservatoryClient = Depends(get_observatory_client),
):
    """
    Check Observatory service health.

    Returns health status with response time. Does not require authentication.

    Returns:
        Health status object

    Example:
        {
            "status": "operational",
            "response_time_ms": 45,
            "last_checked": "2025-01-05T14:32:10Z"
        }
    """
    health_status = await client.health()

    # Return 200 if operational, 503 if degraded/offline
    if health_status["status"] == "operational":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)
