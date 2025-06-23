"""Domain entity fixtures for testing."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_user_2() -> User:
    """Create a second sample user for testing."""
    return User(
        id=uuid4(),
        email="test2@example.com",
        username="testuser2",
        full_name="Test User 2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_task_list(sample_user: User) -> TaskList:
    """Create a sample task list for testing."""
    return TaskList(
        id=uuid4(),
        name="Test Task List",
        description="A test task list",
        owner_id=sample_user.id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_task(sample_task_list: TaskList, sample_user: User) -> Task:
    """Create a sample task for testing."""
    return Task(
        id=uuid4(),
        title="Test Task",
        description="A test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        task_list_id=sample_task_list.id,
        assigned_user_id=sample_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_task_unassigned(sample_task_list: TaskList) -> Task:
    """Create a sample unassigned task for testing."""
    return Task(
        id=uuid4(),
        title="Unassigned Task",
        description="An unassigned test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        task_list_id=sample_task_list.id,
        assigned_user_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def completed_task(sample_task_list: TaskList, sample_user: User) -> Task:
    """Create a completed task for testing."""
    now = datetime.now(timezone.utc)
    return Task(
        id=uuid4(),
        title="Completed Task",
        description="A completed test task",
        status=TaskStatus.COMPLETED,
        priority=TaskPriority.LOW,
        task_list_id=sample_task_list.id,
        assigned_user_id=sample_user.id,
        created_at=now,
        updated_at=now,
        completed_at=now,
    )
