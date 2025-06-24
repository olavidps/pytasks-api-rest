"""Tests for Task domain model."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.models.task import Task, TaskPriority, TaskStatus


class TestTaskModel:
    """Test cases for Task domain model."""

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def task_with_due_date(self):
        """Create a task with due date."""
        return Task(
            id=uuid4(),
            title="Task with Due Date",
            description="Task Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            task_list_id=uuid4(),
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_update_task_title_only(self, sample_task):
        """Test updating only the title of a task."""
        # Arrange
        new_title = "Updated Title"
        original_description = sample_task.description
        original_due_date = sample_task.due_date

        # Act
        updated_task = sample_task.update_details(title=new_title)

        # Assert
        assert updated_task.title == new_title
        assert updated_task.description == original_description
        assert updated_task.due_date == original_due_date
        assert updated_task.updated_at > sample_task.updated_at

    def test_update_task_description_only(self, sample_task):
        """Test updating only the description of a task."""
        # Arrange
        new_description = "Updated Description"
        original_title = sample_task.title
        original_due_date = sample_task.due_date

        # Act
        updated_task = sample_task.update_details(description=new_description)

        # Assert
        assert updated_task.title == original_title
        assert updated_task.description == new_description
        assert updated_task.due_date == original_due_date
        assert updated_task.updated_at > sample_task.updated_at

    def test_update_task_due_date_only(self, sample_task):
        """Test updating only the due date of a task."""
        # Arrange
        new_due_date = datetime.now(timezone.utc) + timedelta(days=7)
        original_title = sample_task.title
        original_description = sample_task.description

        # Act
        updated_task = sample_task.update_details(due_date=new_due_date)

        # Assert
        assert updated_task.title == original_title
        assert updated_task.description == original_description
        assert updated_task.due_date == new_due_date
        assert updated_task.updated_at > sample_task.updated_at

    def test_update_task_all_fields(self, sample_task):
        """Test updating all fields of a task."""
        # Arrange
        new_title = "Completely New Title"
        new_description = "Completely New Description"
        new_due_date = datetime.now(timezone.utc) + timedelta(days=5)

        # Act
        updated_task = sample_task.update_details(
            title=new_title, description=new_description, due_date=new_due_date
        )

        # Assert
        assert updated_task.title == new_title
        assert updated_task.description == new_description
        assert updated_task.due_date == new_due_date
        assert updated_task.updated_at > sample_task.updated_at

    def test_update_task_no_changes(self, sample_task):
        """Test updating task with no changes."""
        # Act
        updated_task = sample_task.update_details()

        # Assert
        assert updated_task.title == sample_task.title
        assert updated_task.description == sample_task.description
        assert updated_task.due_date == sample_task.due_date
        assert updated_task.updated_at > sample_task.updated_at

    def test_is_completed_when_pending(self, sample_task):
        """Test is_completed returns False for pending task."""
        # Assert
        assert not sample_task.is_completed

    def test_is_completed_when_in_progress(self, sample_task):
        """Test is_completed returns False for in progress task."""
        # Arrange
        in_progress_task = sample_task.mark_as_in_progress()

        # Assert
        assert not in_progress_task.is_completed

    def test_is_completed_when_completed(self, sample_task):
        """Test is_completed returns True for completed task."""
        # Arrange
        completed_task = sample_task.mark_as_completed()

        # Assert
        assert completed_task.is_completed

    def test_is_overdue_when_no_due_date(self, sample_task):
        """Test is_overdue returns False when task has no due date."""
        # Assert
        assert not sample_task.is_overdue

    def test_is_overdue_when_due_date_in_future(self, task_with_due_date):
        """Test is_overdue returns False when due date is in the future."""
        # Assert
        assert not task_with_due_date.is_overdue

    def test_is_overdue_when_due_date_in_past(self, sample_task):
        """Test is_overdue returns True when due date is in the past."""
        # Arrange
        past_due_date = datetime.now(timezone.utc) - timedelta(hours=1)
        overdue_task = sample_task.update_details(due_date=past_due_date)

        # Assert
        assert overdue_task.is_overdue

    def test_is_overdue_when_completed_and_past_due(self, sample_task):
        """Test is_overdue returns False when task is completed even if past due."""
        # Arrange
        past_due_date = datetime.now(timezone.utc) - timedelta(hours=1)
        overdue_task = sample_task.update_details(due_date=past_due_date)
        completed_overdue_task = overdue_task.mark_as_completed()

        # Assert
        assert not completed_overdue_task.is_overdue

    def test_is_overdue_when_due_date_is_now(self, sample_task):
        """Test is_overdue behavior when due date is in the future."""
        # Arrange
        future_date = datetime.now(timezone.utc) + timedelta(minutes=1)
        task_due_future = sample_task.update_details(due_date=future_date)

        # Assert
        # Should not be overdue if due date is in the future
        assert not task_due_future.is_overdue

    def test_update_task_preserves_other_attributes(self, sample_task):
        """Test that update preserves other task attributes."""
        # Arrange
        original_id = sample_task.id
        original_status = sample_task.status
        original_priority = sample_task.priority
        original_task_list_id = sample_task.task_list_id
        original_created_at = sample_task.created_at

        # Act
        updated_task = sample_task.update_details(title="New Title")

        # Assert
        assert updated_task.id == original_id
        assert updated_task.status == original_status
        assert updated_task.priority == original_priority
        assert updated_task.task_list_id == original_task_list_id
        assert updated_task.created_at == original_created_at
        assert updated_task.assigned_user_id == sample_task.assigned_user_id
        assert updated_task.completed_at == sample_task.completed_at

    def test_task_immutability_after_update(self, sample_task):
        """Test that original task remains unchanged after update."""
        # Arrange
        original_title = sample_task.title
        original_updated_at = sample_task.updated_at

        # Act
        updated_task = sample_task.update_details(title="New Title")

        # Assert
        assert sample_task.title == original_title
        assert sample_task.updated_at == original_updated_at
        assert updated_task.title == "New Title"
        assert updated_task.updated_at > original_updated_at
