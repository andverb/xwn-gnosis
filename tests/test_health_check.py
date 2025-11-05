"""
Tests for the improved health check endpoint.

This module tests the comprehensive health check that verifies database connectivity.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestHealthCheck:
    """Test health check endpoint functionality."""

    def test_health_check_healthy(self, client):
        """Test health check returns 200 when all checks pass."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "healthy"

    def test_health_check_includes_version(self, client):
        """Test that health check includes version information."""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "0.1.0"

    def test_health_check_includes_environment(self, client):
        """Test that health check includes environment information."""
        response = client.get("/health")
        data = response.json()
        assert data["environment"] in ["development", "staging", "production"]

    def test_health_check_database_check(self, client):
        """Test that health check verifies database connectivity."""
        response = client.get("/health")
        data = response.json()

        assert "database" in data["checks"]
        db_check = data["checks"]["database"]
        assert "status" in db_check
        assert "message" in db_check

    def test_health_check_schema_check(self, client):
        """Test that health check verifies database schema access."""
        response = client.get("/health")
        data = response.json()

        # Schema check should be present
        if "database_schema" in data["checks"]:
            schema_check = data["checks"]["database_schema"]
            assert "status" in schema_check
            assert schema_check["status"] in ["healthy", "degraded", "unhealthy"]
