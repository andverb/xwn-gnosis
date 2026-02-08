"""
Test configuration and fixtures for pytest.

This module provides shared fixtures for testing the Gnosis application,
including database setup, test client, and sample data factories.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.dependencies import AppSettings
from app.main import app
from app.models import Base, Rule, RuleSet

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for the entire test session.

    This is needed for pytest-asyncio to work properly with session-scoped fixtures.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Provide test settings with test database URL.

    Returns:
        Settings instance configured for testing
    """
    return Settings(
        database_url=TEST_DATABASE_URL,
        api_key="test_api_key_12345",
        admin_username="test_admin",
        admin_password="test_password",
        secret_key="test_secret_key_minimum_32_characters_long_for_security",
        environment="development",
        log_level="DEBUG",
        log_json=False,
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Create a test database engine with in-memory SQLite.

    Uses StaticPool to ensure the in-memory database persists across connections.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Enable foreign key constraints in SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for each test.

    Uses transaction-based isolation - all changes are rolled back after each test,
    ensuring complete test isolation even if tests fail mid-execution.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
def client(test_settings: Settings, db_session: AsyncSession) -> TestClient:
    """
    Provide a FastAPI test client with dependency overrides.

    Args:
        test_settings: Test settings fixture
        db_session: Test database session fixture

    Returns:
        TestClient instance for making test requests
    """
    from app.db import get_db

    # Override dependencies
    def override_get_settings() -> Settings:
        return test_settings

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[AppSettings] = override_get_settings
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_ruleset(db_session: AsyncSession) -> RuleSet:
    """
    Create a sample ruleset for testing.

    Returns:
        RuleSet instance saved to the test database
    """
    ruleset = RuleSet(
        name="Test Worlds Without Number",
        slug="test-wwn",
        abbreviation="Test-WWN",
        description="A test ruleset for unit testing",
        is_official=True,
    )
    db_session.add(ruleset)
    await db_session.commit()
    await db_session.refresh(ruleset)
    return ruleset


@pytest_asyncio.fixture
async def sample_rule(db_session: AsyncSession, sample_ruleset: RuleSet) -> Rule:
    """
    Create a sample rule for testing.

    Args:
        db_session: Database session
        sample_ruleset: Parent ruleset

    Returns:
        Rule instance saved to the test database
    """
    rule = Rule(
        name_en="Test Fireball",
        description_en="A test spell that deals fire damage",
        name_uk="Тестова куля вогню",
        description_uk="Тестове закляття, що завдає вогняної шкоди",
        type="spell",
        tags=["fire", "magic", "damage"],
        meta_data={"level": 3, "range": "30 feet"},
        ruleset_id=sample_ruleset.id,
        is_official=True,
    )
    db_session.add(rule)
    await db_session.commit()
    await db_session.refresh(rule)
    return rule


@pytest.fixture
def auth_headers(test_settings: Settings) -> dict[str, str]:
    """
    Provide HTTP Basic Auth headers for authenticated requests.

    Returns:
        Dictionary with Authorization header
    """
    import base64

    credentials = f"{test_settings.admin_username}:{test_settings.admin_password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


@pytest.fixture
def api_key_headers(test_settings: Settings) -> dict[str, str]:
    """
    Provide API key headers for authenticated requests.

    Returns:
        Dictionary with X-API-Key header
    """
    return {"X-API-Key": test_settings.api_key}


@pytest.fixture
def authenticated_client(test_settings: Settings, db_session: AsyncSession) -> TestClient:
    """
    Provide a FastAPI test client with authentication overrides enabled.

    This client bypasses authentication checks for testing authenticated endpoints.
    """
    from app.db import get_db
    from app.dependencies.auth import verify_admin_credentials

    # Override dependencies
    def override_get_settings() -> Settings:
        return test_settings

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Mock admin auth to always succeed
    def override_verify_admin_credentials():
        return "test_admin"

    app.dependency_overrides[AppSettings] = override_get_settings
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_admin_credentials] = override_verify_admin_credentials

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()
