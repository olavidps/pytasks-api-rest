"""Unit tests for TaskRepository implementation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User
from app.infrastructure.repositories.task_list_repository_impl import (
    TaskListRepositoryImpl,
)
from app.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestTaskRepositoryImpl:
    """Test cases for TaskRepositoryImpl."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test successful task creation."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        # Create task
        repo = TaskRepositoryImpl(isolated_db_session)
        created_task = await repo.create(sample_task)

        assert created_task.id == sample_task.id
        assert created_task.title == sample_task.title
        assert created_task.description == sample_task.description
        assert created_task.status == sample_task.status
        assert created_task.priority == sample_task.priority
        assert created_task.task_list_id == sample_task.task_list_id
        assert created_task.assigned_user_id == sample_task.assigned_user_id

    @pytest.mark.asyncio
    async def test_create_unassigned_task(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task_unassigned: Task,
    ):
        """Test creating task without assigned user."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        # Create unassigned task
        repo = TaskRepositoryImpl(isolated_db_session)
        created_task = await repo.create(sample_task_unassigned)

        assert created_task.assigned_user_id is None
        assert created_task.title == sample_task_unassigned.title

    @pytest.mark.asyncio
    async def test_get_by_id_existing_task(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test getting existing task by ID."""
        # Create dependencies and task
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)
        await repo.create(sample_task)

        # Get task by ID
        found_task = await repo.get_by_id(sample_task.id)

        assert found_task is not None
        assert found_task.id == sample_task.id
        assert found_task.title == sample_task.title

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent_task(
        self, isolated_db_session: AsyncSession, sample_task: Task
    ):
        """Test getting nonexistent task by ID returns None."""
        repo = TaskRepositoryImpl(isolated_db_session)

        found_task = await repo.get_by_id(sample_task.id)

        assert found_task is None

    @pytest.mark.asyncio
    async def test_get_by_task_list_id(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test getting tasks by task list ID."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        # Create multiple tasks
        repo = TaskRepositoryImpl(isolated_db_session)

        task_1 = Task(
            title="Task 1",
            description="First task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            task_list_id=sample_task_list.id,
            assigned_user_id=sample_user.id,
        )
        task_2 = Task(
            title="Task 2",
            description="Second task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            task_list_id=sample_task_list.id,
            assigned_user_id=None,
        )

        await repo.create(task_1)
        await repo.create(task_2)

        # Get tasks by task list ID
        tasks = await repo.get_by_task_list_id(sample_task_list.id)

        assert len(tasks) == 2
        task_titles = {task.title for task in tasks}
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles

    @pytest.mark.asyncio
    async def test_get_by_task_list_id_with_filters(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test getting tasks by task list ID with status and priority filters."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        # Create tasks with different statuses and priorities
        repo = TaskRepositoryImpl(isolated_db_session)

        tasks_data = [
            ("Task 1", TaskStatus.PENDING, TaskPriority.HIGH),
            ("Task 2", TaskStatus.PENDING, TaskPriority.MEDIUM),
            ("Task 3", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
            ("Task 4", TaskStatus.COMPLETED, TaskPriority.LOW),
        ]

        for title, status, priority in tasks_data:
            task = Task(
                title=title,
                description=f"Description for {title}",
                status=status,
                priority=priority,
                task_list_id=sample_task_list.id,
                assigned_user_id=sample_user.id,
            )
            await repo.create(task)

        # Filter by status
        pending_tasks = await repo.get_by_task_list_id(
            sample_task_list.id, status=TaskStatus.PENDING
        )
        assert len(pending_tasks) == 2

        # Filter by priority
        high_priority_tasks = await repo.get_by_task_list_id(
            sample_task_list.id, priority=TaskPriority.HIGH
        )
        assert len(high_priority_tasks) == 2

        # Filter by both status and priority
        pending_high_tasks = await repo.get_by_task_list_id(
            sample_task_list.id, status=TaskStatus.PENDING, priority=TaskPriority.HIGH
        )
        assert len(pending_high_tasks) == 1
        assert pending_high_tasks[0].title == "Task 1"

    @pytest.mark.asyncio
    async def test_get_by_assigned_user_id(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_user_2: User,
        sample_task_list: TaskList,
    ):
        """Test getting tasks by assigned user ID."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await user_repo.create(sample_user_2)
        await task_list_repo.create(sample_task_list)

        # Create tasks assigned to different users
        repo = TaskRepositoryImpl(isolated_db_session)

        task_1 = Task(
            title="User 1 Task 1",
            description="Task for user 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=sample_task_list.id,
            assigned_user_id=sample_user.id,
        )
        task_2 = Task(
            title="User 1 Task 2",
            description="Another task for user 1",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            task_list_id=sample_task_list.id,
            assigned_user_id=sample_user.id,
        )
        task_3 = Task(
            title="User 2 Task",
            description="Task for user 2",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW,
            task_list_id=sample_task_list.id,
            assigned_user_id=sample_user_2.id,
        )

        await repo.create(task_1)
        await repo.create(task_2)
        await repo.create(task_3)

        # Get tasks for user 1
        user_1_tasks = await repo.get_by_assigned_user_id(sample_user.id)
        assert len(user_1_tasks) == 2

        # Get tasks for user 2
        user_2_tasks = await repo.get_by_assigned_user_id(sample_user_2.id)
        assert len(user_2_tasks) == 1
        assert user_2_tasks[0].title == "User 2 Task"

    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test successful task update."""
        # Create dependencies and task
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)
        await repo.create(sample_task)

        # Update task
        updated_task = sample_task.model_copy(
            update={
                "title": "Updated Task Title",
                "description": "Updated description",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.HIGH,
            }
        )

        result = await repo.update(updated_task)

        assert result.title == "Updated Task Title"
        assert result.description == "Updated description"
        assert result.status == TaskStatus.IN_PROGRESS
        assert result.priority == TaskPriority.HIGH
        assert result.id == sample_task.id

    @pytest.mark.asyncio
    async def test_update_task_status(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test updating task status to completed."""
        # Create dependencies and task
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)
        await repo.create(sample_task)

        # Mark task as completed
        completed_task = sample_task.mark_as_completed()

        result = await repo.update(completed_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(
        self, isolated_db_session: AsyncSession, sample_task: Task
    ):
        """Test updating nonexistent task raises exception."""
        repo = TaskRepositoryImpl(isolated_db_session)

        with pytest.raises(TaskNotFoundError):
            await repo.update(sample_task)

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test successful task deletion."""
        # Create dependencies and task
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)
        await repo.create(sample_task)

        # Delete task
        result = await repo.delete(sample_task.id)

        assert result is True

        # Verify task is deleted
        found_task = await repo.get_by_id(sample_task.id)
        assert found_task is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(
        self, isolated_db_session: AsyncSession, sample_task: Task
    ):
        """Test deleting nonexistent task returns False."""
        repo = TaskRepositoryImpl(isolated_db_session)

        result = await repo.delete(sample_task.id)

        assert result is False

    @pytest.mark.asyncio
    async def test_count_by_task_list_id(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test counting tasks by task list ID."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)

        # Initially no tasks
        count = await repo.count_by_task_list_id(sample_task_list.id)
        assert count == 0

        # Create some tasks
        for i in range(3):
            task = Task(
                title=f"Task {i}",
                description=f"Description {i}",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                task_list_id=sample_task_list.id,
                assigned_user_id=sample_user.id,
            )
            await repo.create(task)

        # Count should be 3
        count = await repo.count_by_task_list_id(sample_task_list.id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_exists_task(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
        sample_task: Task,
    ):
        """Test checking if task exists."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        repo = TaskRepositoryImpl(isolated_db_session)

        # Check non-existent task
        exists = await repo.exists(sample_task.id)
        assert exists is False

        # Create task
        await repo.create(sample_task)

        # Check existing task
        exists = await repo.exists(sample_task.id)
        assert exists is True

    @pytest.mark.asyncio
    async def test_get_by_task_list_id_with_pagination(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test getting tasks by task list ID with pagination."""
        # Create dependencies
        user_repo = UserRepositoryImpl(isolated_db_session)
        task_list_repo = TaskListRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await task_list_repo.create(sample_task_list)

        # Create multiple tasks
        repo = TaskRepositoryImpl(isolated_db_session)

        for i in range(5):
            task = Task(
                title=f"Task {i}",
                description=f"Description {i}",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                task_list_id=sample_task_list.id,
                assigned_user_id=sample_user.id,
            )
            await repo.create(task)

        # Test pagination
        first_page = await repo.get_by_task_list_id(
            sample_task_list.id, skip=0, limit=2
        )
        assert len(first_page) == 2

        second_page = await repo.get_by_task_list_id(
            sample_task_list.id, skip=2, limit=2
        )
        assert len(second_page) == 2

        third_page = await repo.get_by_task_list_id(
            sample_task_list.id, skip=4, limit=2
        )
        assert len(third_page) == 1
