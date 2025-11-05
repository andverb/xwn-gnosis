"""
Tests for API health and basic endpoint functionality.

This module tests that the API is configured correctly and basic endpoints work.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check and basic endpoints."""

    def test_health_endpoint_exists(self, client: TestClient):
        """Test that health check endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint_exists(self, client: TestClient):
        """Test that root endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_docs_accessible(self, client: TestClient):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON spec is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data


class TestAPIConfiguration:
    """Test API configuration and metadata."""

    def test_api_title_configured(self, client: TestClient):
        """Test that API title is set correctly."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "Gnosis" in data["info"]["title"]

    def test_api_version_configured(self, client: TestClient):
        """Test that API version is set."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "version" in data["info"]
        assert data["info"]["version"] == "0.1.0"

    def test_api_tags_configured(self, client: TestClient):
        """Test that API tags are configured."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "tags" in data
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "rules-api" in tag_names
        assert "rulesets-api" in tag_names
        assert "search-api" in tag_names
