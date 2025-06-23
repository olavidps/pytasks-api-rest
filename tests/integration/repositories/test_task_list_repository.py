"""Unit tests for TaskListRepository implementation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.models.task_list import TaskList
from app.domain.models.user import User
from app.infrastructure.repositories.task_list_repository_impl import (
    TaskListRepositoryImpl,
)
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestTaskListRepositoryImpl:
    """Test cases for TaskListRepositoryImpl."""

    @pytest.mark.asyncio
    async def test_create_task_list_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test successful task list creation."""
        # Create user first
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        # Create task list
        repo = TaskListRepositoryImpl(isolated_db_session)
        created_task_list = await repo.create(sample_task_list)

        assert created_task_list.id == sample_task_list.id
        assert created_task_list.name == sample_task_list.name
        assert created_task_list.description == sample_task_list.description
        assert created_task_list.owner_id == sample_task_list.owner_id
        assert created_task_list.is_active == sample_task_list.is_active

    @pytest.mark.asyncio
    async def test_get_by_id_existing_task_list(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test getting existing task list by ID."""
        # Create user first
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        # Create task list
        repo = TaskListRepositoryImpl(isolated_db_session)
        await repo.create(sample_task_list)

        # Get task list by ID
        found_task_list = await repo.get_by_id(sample_task_list.id)

        assert found_task_list is not None
        assert found_task_list.id == sample_task_list.id
        assert found_task_list.name == sample_task_list.name

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent_task_list(
        self, isolated_db_session: AsyncSession, sample_task_list: TaskList
    ):
        """Test getting nonexistent task list by ID returns None."""
        repo = TaskListRepositoryImpl(isolated_db_session)

        found_task_list = await repo.get_by_id(sample_task_list.id)

        assert found_task_list is None

    @pytest.mark.asyncio
    async def test_get_by_owner_id(
        self, isolated_db_session: AsyncSession, sample_user: User, sample_user_2: User
    ):
        """Test getting task lists by owner ID."""
        # Create users
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)
        await user_repo.create(sample_user_2)

        # Create task lists
        repo = TaskListRepositoryImpl(isolated_db_session)

        task_list_1 = TaskList(
            name="Task List 1",
            description="First task list",
            owner_id=sample_user.id,
            is_active=True,
        )
        task_list_2 = TaskList(
            name="Task List 2",
            description="Second task list",
            owner_id=sample_user.id,
            is_active=True,
        )
        task_list_3 = TaskList(
            name="Task List 3",
            description="Third task list",
            owner_id=sample_user_2.id,
            is_active=True,
        )

        await repo.create(task_list_1)
        await repo.create(task_list_2)
        await repo.create(task_list_3)

        # Get task lists for first user
        user_1_lists = await repo.get_by_owner_id(sample_user.id)

        assert len(user_1_lists) == 2
        list_names = {tl.name for tl in user_1_lists}
        assert "Task List 1" in list_names
        assert "Task List 2" in list_names

        # Get task lists for second user
        user_2_lists = await repo.get_by_owner_id(sample_user_2.id)

        assert len(user_2_lists) == 1
        assert user_2_lists[0].name == "Task List 3"

    @pytest.mark.asyncio
    async def test_get_by_owner_id_with_pagination(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test getting task lists by owner ID with pagination."""
        # Create user
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        # Create multiple task lists
        repo = TaskListRepositoryImpl(isolated_db_session)

        for i in range(5):
            task_list = TaskList(
                name=f"Task List {i}",
                description=f"Task list number {i}",
                owner_id=sample_user.id,
                is_active=True,
            )
            await repo.create(task_list)

        # Test pagination
        first_page = await repo.get_by_owner_id(sample_user.id, skip=0, limit=2)
        assert len(first_page) == 2

        second_page = await repo.get_by_owner_id(sample_user.id, skip=2, limit=2)
        assert len(second_page) == 2

        third_page = await repo.get_by_owner_id(sample_user.id, skip=4, limit=2)
        assert len(third_page) == 1

    @pytest.mark.asyncio
    async def test_update_task_list_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test successful task list update."""
        # Create user first
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        # Create task list
        repo = TaskListRepositoryImpl(isolated_db_session)
        await repo.create(sample_task_list)

        # Update task list
        updated_task_list = sample_task_list.model_copy(
            update={
                "name": "Updated Task List",
                "description": "Updated description",
                "is_active": False,
            }
        )

        result = await repo.update(updated_task_list)

        assert result.name == "Updated Task List"
        assert result.description == "Updated description"
        assert result.is_active is False
        assert result.id == sample_task_list.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_task_list(
        self, isolated_db_session: AsyncSession, sample_task_list: TaskList
    ):
        """Test updating nonexistent task list raises exception."""
        repo = TaskListRepositoryImpl(isolated_db_session)

        with pytest.raises(TaskListNotFoundError):
            await repo.update(sample_task_list)

    @pytest.mark.asyncio
    async def test_delete_task_list_success(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test successful task list deletion."""
        # Create user first
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        # Create task list
        repo = TaskListRepositoryImpl(isolated_db_session)
        await repo.create(sample_task_list)

        # Delete task list
        result = await repo.delete(sample_task_list.id)

        assert result is True

        # Verify task list is deleted
        found_task_list = await repo.get_by_id(sample_task_list.id)
        assert found_task_list is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task_list(
        self, isolated_db_session: AsyncSession, sample_task_list: TaskList
    ):
        """Test deleting nonexistent task list returns False."""
        repo = TaskListRepositoryImpl(isolated_db_session)

        result = await repo.delete(sample_task_list.id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_task_list(
        self,
        isolated_db_session: AsyncSession,
        sample_user: User,
        sample_task_list: TaskList,
    ):
        """Test checking if task list exists."""
        # Create user first
        user_repo = UserRepositoryImpl(isolated_db_session)
        await user_repo.create(sample_user)

        repo = TaskListRepositoryImpl(isolated_db_session)

        # Check non-existent task list
        exists = await repo.exists(sample_task_list.id)
        assert exists is False

        # Create task list
        await repo.create(sample_task_list)

        # Check existing task list
        exists = await repo.exists(sample_task_list.id)
        assert exists is True
