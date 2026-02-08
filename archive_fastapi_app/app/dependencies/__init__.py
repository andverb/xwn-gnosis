"""
Reusable dependency type annotations for FastAPI.

Using Annotated types reduces repetition and makes dependencies more maintainable.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_db

# Database session dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]

# Settings dependency
AppSettings = Annotated[Settings, Depends(get_settings)]
