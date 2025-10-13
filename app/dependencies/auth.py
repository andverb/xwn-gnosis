from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.dependencies import AppSettings

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(settings: AppSettings, api_key: str = Depends(api_key_header)):
    expected_key = settings.api_key
    if not expected_key:
        raise HTTPException(500, "API key not configured")
    if api_key != expected_key:
        raise HTTPException(401, "Invalid API key")
    return api_key
