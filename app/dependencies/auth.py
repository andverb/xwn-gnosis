from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials

from app.dependencies import AppSettings

api_key_header = APIKeyHeader(name="X-API-Key")
http_basic = HTTPBasic()


def verify_api_key(settings: AppSettings, api_key: str = Depends(api_key_header)):
    """Legacy API key authentication (deprecated, kept for backwards compatibility)."""
    expected_key = settings.api_key
    if not expected_key:
        raise HTTPException(500, "API key not configured")
    if api_key != expected_key:
        raise HTTPException(401, "Invalid API key")
    return api_key


def verify_admin_credentials(
    settings: AppSettings,
    credentials: HTTPBasicCredentials = Depends(http_basic),
) -> str:
    """Verify admin username and password via HTTP Basic Auth."""
    if credentials.username != settings.admin_username or credentials.password != settings.admin_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
