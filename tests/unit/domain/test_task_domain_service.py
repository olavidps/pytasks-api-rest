"""Tests for TaskDomainService."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User
from app.domain.services.task_domain_service import TaskDomainService


class TestTaskDomainService:
    """Test cases for TaskDomainService."""

    @pytest.fixture
    def mock_task_repository(self):
        """Create mock task repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_task_list_repository(self):
        """Create mock task list repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def task_domain_service(
        self, mock_task_repository, mock_task_list_repository, mock_user_repository
    ):
        """Create TaskDomainService instance with mocked dependencies."""
        return TaskDomainService(
            task_repository=mock_task_repository,
            task_list_repository=mock_task_list_repository,
            user_repository=mock_user_repository,
        )

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_task_list(self, sample_user):
        """Create a sample task list."""
        return TaskList(
            id=uuid4(),
            name="Test Task List",
            description="Test Description",
            owner_id=sample_user.id,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_task(self, sample_task_list):
        """Create a sample task."""
        return Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=sample_task_list.id,
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


class TestValidateTaskAssignment(TestTaskDomainService):
    """Test validate_task_assignment method."""

    async def test_validate_task_assignment_with_none_user_id(
        self, task_domain_service
    ):
        """Test that unassigning (None user_id) is always valid."""
        task_id = uuid4()
        result = await task_domain_service.validate_task_assignment(task_id, None)
        assert result is True

    async def test_validate_task_assignment_with_active_user(
        self, task_domain_service, mock_user_repository, sample_user
    ):
        """Test assignment to active user is valid."""
        task_id = uuid4()
        mock_user_repository.get_by_id.return_value = sample_user

        result = await task_domain_service.validate_task_assignment(
            task_id, sample_user.id
        )

        assert result is True
        mock_user_repository.get_by_id.assert_called_once_with(sample_user.id)

    async def test_validate_task_assignment_with_inactive_user(
        self, task_domain_service, mock_user_repository, sample_user
    ):
        """Test assignment to inactive user is invalid."""
        task_id = uuid4()
        inactive_user = sample_user.model_copy(update={"is_active": False})
        mock_user_repository.get_by_id.return_value = inactive_user

        result = await task_domain_service.validate_task_assignment(
            task_id, sample_user.id
        )

        assert result is False
        mock_user_repository.get_by_id.assert_called_once_with(sample_user.id)

    async def test_validate_task_assignment_with_nonexistent_user(
        self, task_domain_service, mock_user_repository
    ):
        """Test assignment to nonexistent user is invalid."""
        task_id = uuid4()
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        result = await task_domain_service.validate_task_assignment(task_id, user_id)

        assert result is False
        mock_user_repository.get_by_id.assert_called_once_with(user_id)


class TestValidateTaskListOwnership(TestTaskDomainService):
    """Test validate_task_list_ownership method."""

    async def test_validate_task_list_ownership_valid_owner(
        self,
        task_domain_service,
        mock_task_list_repository,
        sample_task_list,
        sample_user,
    ):
        """Test that owner has access to their task list."""
        mock_task_list_repository.get_by_id.return_value = sample_task_list

        result = await task_domain_service.validate_task_list_ownership(
            sample_task_list.id, sample_user.id
        )

        assert result is True
        mock_task_list_repository.get_by_id.assert_called_once_with(sample_task_list.id)

    async def test_validate_task_list_ownership_different_owner(
        self, task_domain_service, mock_task_list_repository, sample_task_list
    ):
        """Test that non-owner doesn't have access to task list."""
        different_user_id = uuid4()
        mock_task_list_repository.get_by_id.return_value = sample_task_list

        result = await task_domain_service.validate_task_list_ownership(
            sample_task_list.id, different_user_id
        )

        assert result is False
        mock_task_list_repository.get_by_id.assert_called_once_with(sample_task_list.id)

    async def test_validate_task_list_ownership_nonexistent_list(
        self, task_domain_service, mock_task_list_repository
    ):
        """Test that nonexistent task list returns False."""
        task_list_id = uuid4()
        user_id = uuid4()
        mock_task_list_repository.get_by_id.return_value = None

        result = await task_domain_service.validate_task_list_ownership(
            task_list_id, user_id
        )

        assert result is False
        mock_task_list_repository.get_by_id.assert_called_once_with(task_list_id)

    async def test_validate_task_list_ownership_inactive_list(
        self,
        task_domain_service,
        mock_task_list_repository,
        sample_task_list,
        sample_user,
    ):
        """Test that inactive task list returns False."""
        inactive_list = sample_task_list.model_copy(update={"is_active": False})
        mock_task_list_repository.get_by_id.return_value = inactive_list

        result = await task_domain_service.validate_task_list_ownership(
            sample_task_list.id, sample_user.id
        )

        assert result is False
        mock_task_list_repository.get_by_id.assert_called_once_with(sample_task_list.id)


class TestCanTaskBeDeleted(TestTaskDomainService):
    """Test can_task_be_deleted method."""

    async def test_can_task_be_deleted_nonexistent_task(
        self, task_domain_service, mock_task_repository
    ):
        """Test that nonexistent task cannot be deleted."""
        task_id = uuid4()
        mock_task_repository.get_by_id.return_value = None

        can_delete, reason = await task_domain_service.can_task_be_deleted(task_id)

        assert can_delete is False
        assert reason == "Task not found"
        mock_task_repository.get_by_id.assert_called_once_with(task_id)

    async def test_can_task_be_deleted_pending_task(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test that pending task can be deleted."""
        mock_task_repository.get_by_id.return_value = sample_task

        can_delete, reason = await task_domain_service.can_task_be_deleted(
            sample_task.id
        )

        assert can_delete is True
        assert reason == "Task can be deleted"
        mock_task_repository.get_by_id.assert_called_once_with(sample_task.id)

    async def test_can_task_be_deleted_recently_completed_task(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test that recently completed task can be deleted."""
        completed_task = sample_task.mark_as_completed()
        mock_task_repository.get_by_id.return_value = completed_task

        can_delete, reason = await task_domain_service.can_task_be_deleted(
            sample_task.id
        )

        assert can_delete is True
        assert reason == "Task can be deleted"
        mock_task_repository.get_by_id.assert_called_once_with(sample_task.id)

    async def test_can_task_be_deleted_old_completed_task(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test that old completed task should be archived instead of deleted."""
        # Create a task completed 31 days ago
        old_completion_date = datetime.now(timezone.utc) - timedelta(days=31)
        completed_task = sample_task.model_copy(
            update={"status": TaskStatus.COMPLETED, "completed_at": old_completion_date}
        )
        mock_task_repository.get_by_id.return_value = completed_task

        can_delete, reason = await task_domain_service.can_task_be_deleted(
            sample_task.id
        )

        assert can_delete is False
        assert "archived instead of deleted" in reason
        mock_task_repository.get_by_id.assert_called_once_with(sample_task.id)


class TestGetOverdueTasksForUser(TestTaskDomainService):
    """Test get_overdue_tasks_for_user method."""

    async def test_get_overdue_tasks_for_user_no_tasks(
        self, task_domain_service, mock_task_repository
    ):
        """Test getting overdue tasks when user has no tasks."""
        user_id = uuid4()
        mock_task_repository.get_by_assigned_user_id.return_value = []

        result = await task_domain_service.get_overdue_tasks_for_user(user_id)

        assert result == []
        mock_task_repository.get_by_assigned_user_id.assert_called_once_with(user_id)

    async def test_get_overdue_tasks_for_user_with_overdue_tasks(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test getting overdue tasks when user has overdue tasks."""
        user_id = uuid4()
        # Create an overdue task
        overdue_task = sample_task.model_copy(
            update={
                "due_date": datetime.now(timezone.utc) - timedelta(days=1),
                "assigned_user_id": user_id,
            }
        )
        mock_task_repository.get_by_assigned_user_id.return_value = [overdue_task]

        result = await task_domain_service.get_overdue_tasks_for_user(user_id)

        assert len(result) == 1
        assert result[0].id == overdue_task.id
        mock_task_repository.get_by_assigned_user_id.assert_called_once_with(user_id)


class TestCalculateTaskCompletionRate(TestTaskDomainService):
    """Test calculate_task_completion_rate method."""

    async def test_calculate_task_completion_rate_no_tasks(
        self, task_domain_service, mock_task_repository
    ):
        """Test completion rate calculation when no tasks exist."""
        task_list_id = uuid4()
        mock_task_repository.get_by_task_list_id.return_value = []

        result = await task_domain_service.calculate_task_completion_rate(task_list_id)

        assert result == 0.0
        mock_task_repository.get_by_task_list_id.assert_called_once_with(task_list_id)

    async def test_calculate_task_completion_rate_all_completed(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test completion rate when all tasks are completed."""
        task_list_id = uuid4()
        completed_task = sample_task.mark_as_completed()
        mock_task_repository.get_by_task_list_id.return_value = [completed_task]

        result = await task_domain_service.calculate_task_completion_rate(task_list_id)

        assert result == 100.0
        mock_task_repository.get_by_task_list_id.assert_called_once_with(task_list_id)

    async def test_calculate_task_completion_rate_partial_completion(
        self, task_domain_service, mock_task_repository, sample_task
    ):
        """Test completion rate with partial completion."""
        task_list_id = uuid4()
        completed_task = sample_task.mark_as_completed()
        pending_task = sample_task.model_copy(update={"id": uuid4()})
        mock_task_repository.get_by_task_list_id.return_value = [
            completed_task,
            pending_task,
        ]

        result = await task_domain_service.calculate_task_completion_rate(task_list_id)

        assert result == 50.0
        mock_task_repository.get_by_task_list_id.assert_called_once_with(task_list_id)


class TestValidateDueDateConsistency(TestTaskDomainService):
    """Test validate_due_date_consistency method."""

    async def test_validate_due_date_consistency_pending_task(
        self, task_domain_service, sample_task
    ):
        """Test that pending tasks are always consistent."""
        result = await task_domain_service.validate_due_date_consistency(sample_task)
        assert result is True

    async def test_validate_due_date_consistency_completed_before_due(
        self, task_domain_service, sample_task
    ):
        """Test completed task finished before due date."""
        due_date = datetime.now(timezone.utc) + timedelta(days=1)
        completed_date = datetime.now(timezone.utc)
        completed_task = sample_task.model_copy(
            update={
                "status": TaskStatus.COMPLETED,
                "due_date": due_date,
                "completed_at": completed_date,
            }
        )

        result = await task_domain_service.validate_due_date_consistency(completed_task)
        assert result is True

    async def test_validate_due_date_consistency_completed_after_due(
        self, task_domain_service, sample_task
    ):
        """Test completed task finished after due date."""
        due_date = datetime.now(timezone.utc) - timedelta(days=1)
        completed_date = datetime.now(timezone.utc)
        completed_task = sample_task.model_copy(
            update={
                "status": TaskStatus.COMPLETED,
                "due_date": due_date,
                "completed_at": completed_date,
            }
        )

        result = await task_domain_service.validate_due_date_consistency(completed_task)
        assert result is False

    async def test_validate_due_date_consistency_completed_no_due_date(
        self, task_domain_service, sample_task
    ):
        """Test completed task with no due date."""
        completed_task = sample_task.model_copy(
            update={
                "status": TaskStatus.COMPLETED,
                "due_date": None,
                "completed_at": datetime.now(timezone.utc),
            }
        )

        result = await task_domain_service.validate_due_date_consistency(completed_task)
        assert result is True
