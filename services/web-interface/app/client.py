"""
Observatory API client.

HTTP client for proxying requests to Observatory conversation analysis service.
"""
import httpx
from typing import Any
from datetime import datetime
from app.config import settings


class ObservatoryClient:
    """Async HTTP client for Observatory API."""

    def __init__(self, base_url: str | None = None):
        """
        Initialize Observatory client.

        Args:
            base_url: Observatory API base URL (defaults to settings.observatory_url)
        """
        self.base_url = base_url or settings.observatory_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        )

    async def analyze(
        self,
        conversation: list[dict[str, str]],
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        Analyze conversation via Observatory API.

        Args:
            conversation: List of conversation turns with speaker and content
            api_key: Optional Observatory API key for authentication

        Returns:
            Analysis result from Observatory

        Raises:
            httpx.HTTPStatusError: If Observatory returns error status
            httpx.RequestError: If request fails
        """
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = await self.client.post(
            f"{self.base_url}/api/v1/analyze",
            json={"conversation": conversation},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def health(self) -> dict[str, Any]:
        """
        Check Observatory service health.

        Returns:
            Health status with response time

        Example response:
            {
                "status": "operational",
                "response_time_ms": 45,
                "last_checked": "2025-01-05T14:32:10Z"
            }
        """
        try:
            start_time = datetime.now()
            response = await self.client.get(f"{self.base_url}/health")
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            if response.status_code == 200:
                return {
                    "status": "operational",
                    "response_time_ms": elapsed_ms,
                    "last_checked": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "degraded",
                    "response_time_ms": elapsed_ms,
                    "last_checked": datetime.now().isoformat(),
                    "error": f"HTTP {response.status_code}"
                }
        except (httpx.HTTPError, httpx.RequestError) as e:
            return {
                "status": "offline",
                "response_time_ms": -1,
                "last_checked": datetime.now().isoformat(),
                "error": str(e)
            }

    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()


# Dependency for FastAPI routes
async def get_observatory_client() -> ObservatoryClient:
    """
    FastAPI dependency to get Observatory client instance.

    Usage in routes:
        @router.get("/example")
        async def example(client: ObservatoryClient = Depends(get_observatory_client)):
            ...
    """
    client = ObservatoryClient()
    try:
        yield client
    finally:
        await client.close()
