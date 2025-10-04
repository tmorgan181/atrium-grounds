"""Contract tests for GET /examples endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_examples_list_success():
    """Test retrieving list of example conversations."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples")

    assert response.status_code == 200
    data = response.json()

    assert "examples" in data
    assert isinstance(data["examples"], list)
    assert len(data["examples"]) > 0


@pytest.mark.asyncio
async def test_examples_list_structure():
    """Test that example list has correct structure."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples")

    data = response.json()
    example = data["examples"][0]

    # Check required fields
    assert "id" in example
    assert "name" in example
    assert "category" in example
    assert "description" in example
    assert "file" in example
    assert "tags" in example

@pytest.mark.asyncio
async def test_examples_list_categories():
    """Test that categories are included."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples")

    data = response.json()

    assert "categories" in data
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) > 0


@pytest.mark.asyncio
async def test_examples_filter_by_category():
    """Test filtering examples by category."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples?category=dialectic")

    assert response.status_code == 200
    data = response.json()

    # All returned examples should match category
    for example in data["examples"]:
        assert example["category"] == "dialectic"


@pytest.mark.asyncio
async def test_examples_filter_by_difficulty():
    """Test filtering examples by difficulty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples?difficulty=beginner")

    assert response.status_code == 200
    data = response.json()

    # All returned examples should match difficulty
    for example in data["examples"]:
        assert example["difficulty"] == "beginner"


@pytest.mark.asyncio
async def test_examples_invalid_category():
    """Test handling of invalid category filter."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/examples?category=invalid")

    assert response.status_code == 200
    data = response.json()

    # Should return empty list for invalid category
    assert data["examples"] == []
