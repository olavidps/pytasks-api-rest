"""Test configuration and fixtures."""

import asyncio
from datetime import datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import TestingConfig
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User
from app.infrastructure.database.connection import get_db_session
from app.main import app

# Test configuration
test_config = TestingConfig()

# Test database engine with simplified configuration
test_engine = create_async_engine(
    str(test_config.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a database session with transaction rollback."""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    # Create session bound to the connection
    async_session_factory = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    session = async_session_factory()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture(scope="function")
async def isolated_db_session():
    """Create an isolated database session with transactional rollback."""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    # Create session bound to the connection
    async_session_factory = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    session = async_session_factory()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
def client(db_session) -> TestClient:
    """Create a test client with database dependency override."""

    def override_get_db():
        return db_session

    app.dependency_overrides[get_db_session] = override_get_db
    return TestClient(app)


@pytest_asyncio.fixture
async def test_factory(isolated_db_session):
    """Create a test data factory instance with automatic cleanup."""
    from tests.factories.test_data_factory import DataFactory

    factory = DataFactory(isolated_db_session)
    yield factory
    # Cleanup is handled by the session rollback in isolated_db_session fixture


# Simple non-async fixtures for basic test data
@pytest.fixture
def sample_user():
    """Create a sample user object for testing."""
    return User(
        id=uuid4(),
        email=f"test_{uuid4().hex[:8]}@example.com",
        username=f"testuser_{uuid4().hex[:8]}",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_user_2():
    """Create a second sample user object for testing."""
    return User(
        id=uuid4(),
        email=f"test2_{uuid4().hex[:8]}@example.com",
        username=f"testuser2_{uuid4().hex[:8]}",
        full_name="Test User 2",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_task_list(sample_user):
    """Create a sample task list object for testing."""
    return TaskList(
        id=uuid4(),
        name=f"Test Task List {uuid4().hex[:8]}",
        description="A task list for testing",
        owner_id=sample_user.id,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_task(sample_task_list, sample_user):
    """Create a sample task object for testing."""
    return Task(
        id=uuid4(),
        title=f"Test Task {uuid4().hex[:8]}",
        description="A task for testing",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        task_list_id=sample_task_list.id,
        assigned_user_id=sample_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_task_unassigned(sample_task_list):
    """Create a sample unassigned task for testing."""
    return Task(
        id=uuid4(),
        title=f"Unassigned Task {uuid4().hex[:8]}",
        description="An unassigned test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        task_list_id=sample_task_list.id,
        assigned_user_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# Event loop configuration for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
