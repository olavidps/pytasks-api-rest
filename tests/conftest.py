"""Test configuration and fixtures."""

import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.infrastructure.database.connection import get_db_session
from app.main import app

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["TEST_DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/pytasks_test"
)


# Event loop fixture removed - pytest-asyncio handles this automatically in auto mode


@pytest.fixture(scope="session")
def database_url() -> str:
    """Return the database URL for testing."""
    return str(get_settings().DATABASE_URL)


@pytest.fixture(scope="session")
async def engine(database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create a database engine for testing."""
    engine = create_async_engine(
        database_url,
        echo=True,
        poolclass=NullPool,  # Prevents concurrent session conflicts
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Set up the database for testing."""
    # Tables are already created by Alembic migrations
    # Just yield to maintain the fixture structure
    yield


@pytest.fixture(scope="function")
async def db_session(
    engine: AsyncEngine, setup_database: None
) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for testing."""
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        # Clean database before each test
        await session.execute(
            text("TRUNCATE TABLE tasks, task_lists, users RESTART IDENTITY CASCADE")
        )
        await session.commit()

        yield session

        # Clean up after each test
        await session.execute(
            text("TRUNCATE TABLE tasks, task_lists, users RESTART IDENTITY CASCADE")
        )
        await session.commit()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""

    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Only clear the database session override, not all overrides
    if get_db_session in app.dependency_overrides:
        del app.dependency_overrides[get_db_session]
