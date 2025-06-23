import asyncio

import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import TestingConfig
from app.infrastructure.database.connection import Base, get_db_session
from app.main import app
from tests.factories.test_data_factory import DataFactory

# Test engine configuration
test_config = TestingConfig()
test_engine = create_async_engine(
    str(test_config.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Set up the database for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Provide a transactional database session for tests."""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_factory(db_session: AsyncSession) -> DataFactory:
    """Provide a data factory for creating test data."""
    return DataFactory(db_session)


@pytest_asyncio.fixture(scope="function")
def client(db_session: AsyncSession) -> TestClient:
    """Provide a synchronous HTTP client for API tests."""
    yield TestClient(app)
