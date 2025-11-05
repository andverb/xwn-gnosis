from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Log database engine configuration
logger.info(
    "database_engine_configured",
    environment=settings.environment,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=settings.environment == "development",
)

engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL queries in dev for debugging
    pool_size=5,  # Keep 5 persistent connections open
    max_overflow=10,  # Allow 10 additional temporary connections during spikes (15 total)
    pool_pre_ping=True,  # Verify connection health before use (prevents "connection closed" errors)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections from Railway/cloud timeouts)
)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


async def get_db():
    """
    Database session dependency for FastAPI.

    Yields an async database session that automatically commits on success
    and rolls back on exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("database_session_error", error=str(e), error_type=type(e).__name__)
            await session.rollback()
            raise
