"""Basic API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data


@pytest.mark.asyncio
async def test_home_page(client: AsyncClient):
    """Test the home page loads."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_api_docs(client: AsyncClient):
    """Test that API documentation is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_rulesets(client: AsyncClient):
    """Test listing rulesets endpoint."""
    response = await client.get("/api/rulesets/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_rules(client: AsyncClient):
    """Test listing rules endpoint."""
    response = await client.get("/api/rules/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient):
    """Test the search endpoint."""
    response = await client.get("/api/search/?q=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
