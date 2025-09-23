import os

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(api_key: str = Depends(api_key_header)):
    expected_key = os.getenv("GNOSIS_API_KEY")
    if not expected_key:
        raise HTTPException(500, "API key not configured")
    if api_key != expected_key:
        raise HTTPException(401, "Invalid API key")
    return api_key
