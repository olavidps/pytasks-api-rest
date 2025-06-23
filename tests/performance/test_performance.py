"""Performance and concurrency tests for the task management system."""

import time
from datetime import datetime
from uuid import uuid4

import pytest
import pytest_asyncio

from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User
from app.infrastructure.repositories.task_list_repository_impl import (
    TaskListRepositoryImpl,
)
from app.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestPerformance:
    """Performance tests for repository operations."""

    @pytest_asyncio.fixture
    async def sample_user_async(self, isolated_db_session):
        """Create a sample user for async testing."""
        user_repo = UserRepositoryImpl(isolated_db_session)
        user = User(
            id=uuid4(),
            email=f"test-{uuid4()}@example.com",  # Unique email per test
            username=f"testuser-{uuid4()}",  # Unique username per test
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return await user_repo.create(user)

    @pytest.mark.asyncio
    async def test_bulk_user_creation_performance(self, isolated_db_session):
        """Test performance of creating multiple users."""
        user_repo = UserRepositoryImpl(isolated_db_session)
        num_users = 100

        start_time = time.time()

        users = []
        for i in range(num_users):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                username=f"user{i}",
                full_name=f"User {i}",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            created_user = await user_repo.create(user)
            users.append(created_user)

        end_time = time.time()
        execution_time = end_time - start_time

        # Should create 100 users in reasonable time (less than 5 seconds)
        assert execution_time < 5.0
        assert len(users) == num_users

        # Verify all users were created
        all_users = await user_repo.list_all()
        assert len(all_users) == num_users

    @pytest.mark.asyncio
    async def test_bulk_task_creation_performance(
        self, isolated_db_session, sample_user_async
    ):
        """Test performance of creating multiple tasks."""
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        task_repo = TaskRepositoryImpl(isolated_db_session)

        # Create a task list first
        task_list = TaskList(
            id=uuid4(),
            name="Performance Test List",
            description="List for performance testing",
            owner_id=sample_user_async.id,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created_list = await task_list_repo.create(task_list)

        num_tasks = 200
        start_time = time.time()

        tasks = []
        for i in range(num_tasks):
            task = Task(
                id=uuid4(),
                title=f"Performance Task {i}",
                description=f"Task {i} for performance testing",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                task_list_id=created_list.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            created_task = await task_repo.create(task)
            tasks.append(created_task)

        end_time = time.time()
        execution_time = end_time - start_time

        # Should create 200 tasks in reasonable time (less than 10 seconds)
        assert execution_time < 10.0
        assert len(tasks) == num_tasks

        # Verify all tasks were created
        all_tasks = await task_repo.get_by_task_list_id(
            created_list.id, limit=num_tasks
        )
        assert len(all_tasks) == num_tasks

    @pytest.mark.asyncio
    async def test_pagination_performance(self, isolated_db_session, sample_user_async):
        """Test performance of paginated queries."""
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        task_repo = TaskRepositoryImpl(isolated_db_session)

        # Create a task list
        task_list = TaskList(
            id=uuid4(),
            name="Pagination Test List",
            description="List for pagination testing",
            owner_id=sample_user_async.id,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created_list = await task_list_repo.create(task_list)

        # Create 500 tasks
        for i in range(500):
            task = Task(
                id=uuid4(),
                title=f"Pagination Task {i}",
                description=f"Task {i} for pagination testing",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                task_list_id=created_list.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            await task_repo.create(task)

        # Test pagination performance
        start_time = time.time()

        # Get first page
        page_1 = await task_repo.get_by_task_list_id(created_list.id, limit=50, skip=0)

        # Get middle page
        page_10 = await task_repo.get_by_task_list_id(
            created_list.id, limit=50, skip=450
        )

        # Get last page
        page_last = await task_repo.get_by_task_list_id(
            created_list.id, limit=50, skip=450
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Pagination should be fast (less than 1 second)
        assert execution_time < 1.0
        assert len(page_1) == 50
        assert len(page_10) == 50
        assert len(page_last) == 50
