"""Unit tests for task use cases.

These tests mock all dependencies and focus on testing the business logic
of task use cases in isolation.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.delete_task import DeleteTaskUseCase
from app.application.use_cases.get_task import GetTaskUseCase
from app.application.use_cases.get_tasks import GetTasksUseCase
from app.application.use_cases.update_task import UpdateTaskUseCase
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User


class TestCreateTaskUseCase:
    """Test cases for CreateTaskUseCase."""

    @pytest.fixture
    def mock_task_repository(self):
        """Mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_task_validation_service(self):
        """Mock task validation service."""
        return AsyncMock()

    @pytest.fixture
    def create_task_use_case(self, mock_task_repository, mock_task_validation_service):
        """Create task use case instance with mocked dependencies."""
        return CreateTaskUseCase(
            task_repository=mock_task_repository,
            task_validation_service=mock_task_validation_service,
        )

    @pytest.fixture
    def sample_task(self):
        """Sample task for testing."""
        return Task(
            title="Test Task",
            description="Test description",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            task_list_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        create_task_use_case,
        mock_task_repository,
        mock_task_validation_service,
        sample_task,
    ):
        """Test successful task creation."""
        # Arrange
        creator_user_id = uuid.uuid4()
        created_task = Task(
            id=uuid.uuid4(),
            title=sample_task.title,
            description=sample_task.description,
            priority=sample_task.priority,
            status=sample_task.status,
            task_list_id=sample_task.task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_task_validation_service.validate_task_creation.return_value = None
        mock_task_repository.create.return_value = created_task

        # Act
        result = await create_task_use_case.execute(sample_task, creator_user_id)

        # Assert
        assert result == created_task
        mock_task_validation_service.validate_task_creation.assert_called_once_with(
            sample_task, creator_user_id
        )
        mock_task_repository.create.assert_called_once_with(sample_task)

    @pytest.mark.asyncio
    async def test_execute_validation_failure(
        self,
        create_task_use_case,
        mock_task_repository,
        mock_task_validation_service,
        sample_task,
    ):
        """Test task creation with validation failure."""
        # Arrange
        creator_user_id = uuid.uuid4()
        mock_task_validation_service.validate_task_creation.side_effect = ValueError(
            "Invalid task data"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid task data"):
            await create_task_use_case.execute(sample_task, creator_user_id)

        mock_task_repository.create.assert_not_called()


class TestGetTaskUseCase:
    """Test cases for GetTaskUseCase."""

    @pytest.fixture
    def mock_task_repository(self):
        """Mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_task_list_repository(self):
        """Mock task list repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def get_task_use_case(
        self, mock_task_repository, mock_task_list_repository, mock_user_repository
    ):
        """Get task use case instance with mocked dependencies."""
        return GetTaskUseCase(
            task_repository=mock_task_repository,
            task_list_repository=mock_task_list_repository,
            user_repository=mock_user_repository,
        )

    @pytest.fixture
    def sample_task(self):
        """Sample task for testing."""
        return Task(
            id=uuid.uuid4(),
            title="Test Task",
            description="Test description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            task_list_id=uuid.uuid4(),
            assigned_user_id=uuid.uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @pytest.fixture
    def sample_task_list(self, sample_task):
        """Sample task list for testing."""
        return TaskList(
            id=sample_task.task_list_id,
            name="Test Task List",
            description="Test description",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @pytest.fixture
    def sample_user(self, sample_task):
        """Sample user for testing."""
        return User(
            id=sample_task.assigned_user_id,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        get_task_use_case,
        mock_task_repository,
        mock_task_list_repository,
        mock_user_repository,
        sample_task,
        sample_task_list,
        sample_user,
    ):
        """Test successful task retrieval with relations."""
        # Arrange
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_list_repository.get_by_id.return_value = sample_task_list
        mock_user_repository.get_by_id.return_value = sample_user

        # Act
        result = await get_task_use_case.execute(sample_task.id)

        # Assert
        assert result.id == sample_task.id
        assert result.title == sample_task.title
        mock_task_repository.get_by_id.assert_called_once_with(sample_task.id)
        mock_task_list_repository.get_by_id.assert_called_once_with(
            sample_task.task_list_id
        )
        mock_user_repository.get_by_id.assert_called_once_with(
            sample_task.assigned_user_id
        )

    @pytest.mark.asyncio
    async def test_execute_task_not_found(
        self,
        get_task_use_case,
        mock_task_repository,
        mock_task_list_repository,
        mock_user_repository,
    ):
        """Test task retrieval when task doesn't exist."""
        # Arrange
        task_id = uuid.uuid4()
        mock_task_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(
            TaskNotFoundError, match=f"Task with id {task_id} not found"
        ):
            await get_task_use_case.execute(task_id)

        mock_task_list_repository.get_by_id.assert_not_called()
        mock_user_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_task_list_not_found(
        self,
        get_task_use_case,
        mock_task_repository,
        mock_task_list_repository,
        mock_user_repository,
        sample_task,
    ):
        """Test task retrieval when task list doesn't exist."""
        # Arrange
        mock_task_repository.get_by_id.return_value = sample_task
        mock_task_list_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(
            TaskNotFoundError,
            match=f"Task list with id {sample_task.task_list_id} not found for task {sample_task.id}",
        ):
            await get_task_use_case.execute(sample_task.id)

        mock_user_repository.get_by_id.assert_not_called()


class TestUpdateTaskUseCase:
    """Test cases for UpdateTaskUseCase."""

    @pytest.fixture
    def mock_task_repository(self):
        """Mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_task_validation_service(self):
        """Mock task validation service."""
        return AsyncMock()

    @pytest.fixture
    def update_task_use_case(self, mock_task_repository, mock_task_validation_service):
        """Update task use case instance with mocked dependencies."""
        return UpdateTaskUseCase(
            task_repository=mock_task_repository,
            task_validation_service=mock_task_validation_service,
        )

    @pytest.fixture
    def existing_task(self):
        """Existing task for testing."""
        return Task(
            id=uuid.uuid4(),
            title="Original Task",
            description="Original description",
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING,
            task_list_id=uuid.uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        update_task_use_case,
        mock_task_repository,
        mock_task_validation_service,
        existing_task,
    ):
        """Test successful task update."""
        # Arrange
        update_task_data = Task(
            title="Updated Task",
            description="Updated description",
            priority=TaskPriority.HIGH,
            status=existing_task.status,
            task_list_id=existing_task.task_list_id,
        )

        updated_task = Task(
            id=existing_task.id,
            title=update_task_data.title,
            description=update_task_data.description,
            priority=update_task_data.priority,
            status=existing_task.status,
            task_list_id=existing_task.task_list_id,
            created_at=existing_task.created_at,
            updated_at=datetime.now(),
        )

        mock_task_repository.get_by_id.return_value = existing_task
        mock_task_validation_service.validate_task_update.return_value = None
        mock_task_repository.update.return_value = updated_task

        # Act
        result = await update_task_use_case.execute(existing_task.id, update_task_data)

        # Assert
        assert result == updated_task
        mock_task_repository.get_by_id.assert_called_once_with(existing_task.id)
        mock_task_validation_service.validate_task_update.assert_called_once()
        mock_task_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_task_not_found(
        self,
        update_task_use_case,
        mock_task_repository,
        mock_task_validation_service,
    ):
        """Test task update when task doesn't exist."""
        # Arrange
        task_id = uuid.uuid4()
        update_task_data = Task(
            title="Updated Task",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            task_list_id=uuid.uuid4(),
        )
        mock_task_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(
            TaskNotFoundError, match=f"Task with id {task_id} not found"
        ):
            await update_task_use_case.execute(task_id, update_task_data)

        mock_task_validation_service.validate_task_update.assert_not_called()
        mock_task_repository.update.assert_not_called()


class TestDeleteTaskUseCase:
    """Test cases for DeleteTaskUseCase."""

    @pytest.fixture
    def mock_task_repository(self):
        """Mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_task_validation_service(self):
        """Mock task validation service."""
        return AsyncMock()

    @pytest.fixture
    def delete_task_use_case(self, mock_task_repository, mock_task_validation_service):
        """Delete task use case instance with mocked dependencies."""
        return DeleteTaskUseCase(
            task_repository=mock_task_repository,
            task_validation_service=mock_task_validation_service,
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self, delete_task_use_case, mock_task_repository, mock_task_validation_service
    ):
        """Test successful task deletion."""
        # Arrange
        task_id = uuid.uuid4()

        mock_task_validation_service.validate_task_deletion.return_value = None
        mock_task_repository.delete.return_value = True

        # Act
        await delete_task_use_case.execute(task_id)

        # Assert
        mock_task_validation_service.validate_task_deletion.assert_called_once_with(
            task_id
        )
        mock_task_repository.delete.assert_called_once_with(task_id)

    @pytest.mark.asyncio
    async def test_execute_validation_failure(
        self, delete_task_use_case, mock_task_repository, mock_task_validation_service
    ):
        """Test task deletion with validation failure."""
        # Arrange
        task_id = uuid.uuid4()
        mock_task_validation_service.validate_task_deletion.side_effect = (
            TaskNotFoundError(f"Task with id {task_id} not found")
        )

        # Act & Assert
        with pytest.raises(
            TaskNotFoundError, match=f"Task with id {task_id} not found"
        ):
            await delete_task_use_case.execute(task_id)

        mock_task_repository.delete.assert_not_called()


class TestGetTasksUseCase:
    """Test cases for GetTasksUseCase."""

    @pytest.fixture
    def mock_task_repository(self):
        """Mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def get_tasks_use_case(self, mock_task_repository):
        """Get tasks use case instance with mocked dependencies."""
        return GetTasksUseCase(task_repository=mock_task_repository)

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        task_list_id = uuid.uuid4()
        return [
            Task(
                id=uuid.uuid4(),
                title=f"Task {i}",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                task_list_id=task_list_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(3)
        ]

    @pytest.fixture
    def pagination_params(self):
        """Mock pagination parameters."""
        pagination = Mock()
        pagination.page = 1
        pagination.size = 10
        return pagination

    @pytest.mark.asyncio
    async def test_execute_success(
        self, get_tasks_use_case, mock_task_repository, sample_tasks, pagination_params
    ):
        """Test successful tasks retrieval with pagination."""
        # Arrange
        filters = {"task_list_id": sample_tasks[0].task_list_id}
        total_count = len(sample_tasks)

        mock_task_repository.get_paginated.return_value = (
            sample_tasks,
            total_count,
        )

        # Act
        result_tasks, result_total = await get_tasks_use_case.execute(
            pagination=pagination_params, filters=filters
        )

        # Assert
        assert result_tasks == sample_tasks
        assert result_total == total_count
        mock_task_repository.get_paginated.assert_called_once_with(
            offset=0,  # (page - 1) * size = (1 - 1) * 10 = 0
            limit=10,
            filters=filters,
        )

    @pytest.mark.asyncio
    async def test_execute_with_filters(
        self, get_tasks_use_case, mock_task_repository, sample_tasks, pagination_params
    ):
        """Test tasks retrieval with filters."""
        # Arrange
        filters = {
            "task_list_id": uuid.uuid4(),
            "status": TaskStatus.COMPLETED,
            "priority": TaskPriority.HIGH,
        }
        filtered_tasks = [sample_tasks[0]]  # Only one task matches filters

        mock_task_repository.get_paginated.return_value = (
            filtered_tasks,
            len(filtered_tasks),
        )

        # Act
        result_tasks, result_total = await get_tasks_use_case.execute(
            pagination=pagination_params, filters=filters
        )

        # Assert
        assert result_tasks == filtered_tasks
        assert result_total == len(filtered_tasks)
        mock_task_repository.get_paginated.assert_called_once_with(
            offset=0,
            limit=10,
            filters=filters,
        )

    @pytest.mark.asyncio
    async def test_execute_invalid_pagination(
        self, get_tasks_use_case, mock_task_repository
    ):
        """Test tasks retrieval with invalid pagination parameters."""
        # Arrange
        invalid_pagination = Mock()
        invalid_pagination.page = 0  # Invalid page
        invalid_pagination.size = 10
        filters = {}

        # Act & Assert
        with pytest.raises(ValueError, match="Page number must be greater than 0"):
            await get_tasks_use_case.execute(
                pagination=invalid_pagination, filters=filters
            )

        mock_task_repository.get_paginated.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_invalid_page_size(
        self, get_tasks_use_case, mock_task_repository
    ):
        """Test tasks retrieval with invalid page size."""
        # Arrange
        invalid_pagination = Mock()
        invalid_pagination.page = 1
        invalid_pagination.size = 0  # Invalid size
        filters = {}

        # Act & Assert
        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            await get_tasks_use_case.execute(
                pagination=invalid_pagination, filters=filters
            )

        mock_task_repository.get_paginated.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_empty_result(
        self, get_tasks_use_case, mock_task_repository, pagination_params
    ):
        """Test tasks retrieval when no tasks exist."""
        # Arrange
        filters = {"task_list_id": uuid.uuid4()}
        mock_task_repository.get_paginated.return_value = ([], 0)

        # Act
        result_tasks, result_total = await get_tasks_use_case.execute(
            pagination=pagination_params, filters=filters
        )

        # Assert
        assert result_tasks == []
        assert result_total == 0
