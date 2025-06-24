"""Unit tests for task repository."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl


class TestTaskRepository:
    """Test cases for TaskRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock async database session."""
        session = MagicMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def task_repository(self, mock_session):
        """Task repository instance."""
        return TaskRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            assigned_user_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def test_create_task_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful task creation."""
        # Arrange
        task_repository._to_domain = MagicMock(return_value=sample_task)

        # Act
        result = await task_repository.create(sample_task)

        # Assert
        assert isinstance(result, Task)
        assert result.id == sample_task.id
        assert result.title == sample_task.title
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_get_by_id_success(self, task_repository, mock_session, sample_task):
        """Test successful task retrieval by ID."""
        # Arrange
        mock_task_model = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task_model
        mock_session.execute.return_value = mock_result
        task_repository._to_domain = MagicMock(return_value=sample_task)

        # Act
        result = await task_repository.get_by_id(str(sample_task.id))

        # Assert
        assert result == sample_task
        mock_session.execute.assert_called_once()
        task_repository._to_domain.assert_called_once_with(mock_task_model)

    async def test_get_by_id_not_found(self, task_repository, mock_session):
        """Test task retrieval when task doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await task_repository.get_by_id(str(uuid4()))

    async def test_update_task_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful task update."""
        # Arrange
        mock_task_model = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task_model
        mock_session.execute.return_value = mock_result

        updated_task = sample_task.update_details(title="Updated Title")
        task_repository._to_domain = MagicMock(return_value=updated_task)

        # Act
        result = await task_repository.update(updated_task)

        # Assert
        assert result == updated_task
        assert mock_task_model.title == "Updated Title"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_task_model)

    async def test_update_task_not_found(
        self, task_repository, mock_session, sample_task
    ):
        """Test task update when task doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await task_repository.update(sample_task)

    async def test_delete_task_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful task deletion."""
        # Arrange
        mock_task_model = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task_model
        mock_session.execute.return_value = mock_result

        # Act
        await task_repository.delete(str(sample_task.id))

        # Assert
        mock_session.delete.assert_called_once_with(mock_task_model)
        mock_session.commit.assert_called_once()

    async def test_delete_task_not_found(self, task_repository, mock_session):
        """Test task deletion when task doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await task_repository.delete(str(uuid4()))

    async def test_get_by_task_list_id_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful task retrieval by task list ID."""
        # Arrange
        mock_task_models = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_task_models
        mock_session.execute.return_value = mock_result

        tasks = [sample_task, sample_task]
        task_repository._to_domain = MagicMock(side_effect=tasks)

        # Act
        result = await task_repository.get_by_task_list_id(
            str(sample_task.task_list_id)
        )

        # Assert
        assert len(result) == 2
        assert all(isinstance(task, Task) for task in result)
        mock_session.execute.assert_called_once()

    async def test_get_by_assigned_user_id_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful task retrieval by assigned user ID."""
        # Arrange
        mock_task_models = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_task_models
        mock_session.execute.return_value = mock_result

        task_repository._to_domain = MagicMock(return_value=sample_task)

        # Act
        result = await task_repository.get_by_assigned_user_id(
            str(sample_task.assigned_user_id)
        )

        # Assert
        assert len(result) == 1
        assert result[0] == sample_task
        mock_session.execute.assert_called_once()

    async def test_exists_task_true(self, task_repository, mock_session):
        """Test task existence check returns True."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result

        # Act
        result = await task_repository.exists(str(uuid4()))

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()

    async def test_exists_task_false(self, task_repository, mock_session):
        """Test task existence check returns False."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        # Act
        result = await task_repository.exists(str(uuid4()))

        # Assert
        assert result is False
        mock_session.execute.assert_called_once()

    async def test_count_by_task_list_id_success(self, task_repository, mock_session):
        """Test successful task count by task list ID."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        # Act
        result = await task_repository.count_by_task_list_id(uuid4())

        # Assert
        assert result == 5
        mock_session.execute.assert_called_once()

    async def test_count_by_task_list_id_with_status_filter(
        self, task_repository, mock_session
    ):
        """Test task count by task list ID with status filter."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 3
        mock_session.execute.return_value = mock_result

        # Act
        result = await task_repository.count_by_task_list_id(
            uuid4(), TaskStatus.COMPLETED
        )

        # Assert
        assert result == 3
        mock_session.execute.assert_called_once()

    async def test_get_paginated_success(
        self, task_repository, mock_session, sample_task
    ):
        """Test successful paginated task retrieval."""
        # Arrange
        mock_task_models = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_task_models

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 10

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        tasks = [sample_task, sample_task]
        task_repository._to_domain = MagicMock(side_effect=tasks)

        # Act
        result_tasks, total = await task_repository.get_paginated(offset=0, limit=2)

        # Assert
        assert len(result_tasks) == 2
        assert total == 10
        assert all(isinstance(task, Task) for task in result_tasks)
        assert mock_session.execute.call_count == 2

    async def test_get_paginated_with_filters(
        self, task_repository, mock_session, sample_task
    ):
        """Test paginated task retrieval with filters."""
        # Arrange
        mock_task_models = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_task_models

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_session.execute.side_effect = [mock_count_result, mock_result]

        task_repository._to_domain = MagicMock(return_value=sample_task)

        filters = {
            "task_list_id": str(sample_task.task_list_id),
            "status": TaskStatus.PENDING,
        }

        # Act
        result_tasks, total = await task_repository.get_paginated(
            offset=0, limit=10, filters=filters
        )

        # Assert
        assert len(result_tasks) == 1
        assert total == 1
        assert result_tasks[0] == sample_task
        assert mock_session.execute.call_count == 2
