"""Tests for authentication dependencies."""

import pytest
from fastapi import HTTPException

from app.dependencies.auth import verify_admin_credentials, verify_api_key


class TestAPIKeyAuth:
    """Test API key authentication."""

    def test_valid_api_key(self, test_settings):
        """Test that valid API key is accepted."""
        result = verify_api_key(test_settings, test_settings.api_key)
        assert result == test_settings.api_key

    def test_invalid_api_key(self, test_settings):
        """Test that invalid API key is rejected."""
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(test_settings, "invalid_key")
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value.detail)

    def test_missing_api_key_config(self, test_settings):
        """Test that missing API key configuration raises error."""
        # Temporarily set api_key to None
        original_key = test_settings.api_key
        test_settings.api_key = None

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(test_settings, "any_key")
        assert exc_info.value.status_code == 500
        assert "API key not configured" in str(exc_info.value.detail)

        # Restore original key
        test_settings.api_key = original_key


class TestAdminAuth:
    """Test admin authentication."""

    def test_valid_credentials(self, test_settings):
        """Test that valid admin credentials are accepted."""
        from fastapi.security import HTTPBasicCredentials

        credentials = HTTPBasicCredentials(username=test_settings.admin_username, password=test_settings.admin_password)
        result = verify_admin_credentials(test_settings, credentials)
        assert result == test_settings.admin_username

    def test_invalid_username(self, test_settings):
        """Test that invalid username is rejected."""
        from fastapi.security import HTTPBasicCredentials

        credentials = HTTPBasicCredentials(username="wrong_user", password=test_settings.admin_password)
        with pytest.raises(HTTPException) as exc_info:
            verify_admin_credentials(test_settings, credentials)
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)

    def test_invalid_password(self, test_settings):
        """Test that invalid password is rejected."""
        from fastapi.security import HTTPBasicCredentials

        credentials = HTTPBasicCredentials(username=test_settings.admin_username, password="wrong_password")
        with pytest.raises(HTTPException) as exc_info:
            verify_admin_credentials(test_settings, credentials)
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)

    def test_invalid_credentials_both(self, test_settings):
        """Test that both username and password wrong is rejected."""
        from fastapi.security import HTTPBasicCredentials

        credentials = HTTPBasicCredentials(username="wrong_user", password="wrong_password")
        with pytest.raises(HTTPException) as exc_info:
            verify_admin_credentials(test_settings, credentials)
        assert exc_info.value.status_code == 401
