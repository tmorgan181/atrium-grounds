"""Contract tests for GET /examples/{name} endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport



@pytest.mark.asyncio
async def test_get_example_by_id_success(app):
    """Test retrieving a specific example conversation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/philosophical-inquiry")

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["id"] == "philosophical-inquiry"
    assert "content" in data
    assert "metadata" in data


@pytest.mark.asyncio
async def test_get_example_content(app):
    """Test that example content is returned."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/technical-assistance")

    data = response.json()

    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0
    # Should contain the conversation
    assert "Human:" in data["content"] or "AI:" in data["content"]


@pytest.mark.asyncio
async def test_get_example_metadata(app):
    """Test that metadata is included."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/dialectic-exchange")

    data = response.json()
    metadata = data["metadata"]

    assert "name" in metadata
    assert "category" in metadata
    assert "description" in metadata
    assert "tags" in metadata
    assert "expected_patterns" in metadata


@pytest.mark.asyncio
async def test_get_example_not_found(app):
    """Test handling of non-existent example."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/nonexistent-example")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_example_invalid_id_format(app):
    """Test handling of invalid ID format."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/invalid!@#$")

    # Should return 404 for invalid format
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_example_with_analyze_link(app):
    """Test that example includes link to analyze endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples/emotional-support")

    data = response.json()

    # Should include a way to analyze this example
    assert "analyze_url" in data or "links" in data
