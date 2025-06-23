"""Unit tests for edge cases and boundary conditions."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User


class TestEdgeCases:
    """Test edge cases and boundary conditions for domain models."""

    def test_task_with_empty_title_validation(self):
        """Test task creation with empty title should raise validation error."""
        with pytest.raises(ValueError):
            Task(
                id=uuid4(),
                title="",  # Empty title
                description="Valid description",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                task_list_id=uuid4(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_task_with_whitespace_only_title(self):
        """Test task creation with whitespace-only title is allowed by current validation."""
        # Current validation only checks min_length=1, so whitespace is allowed
        task = Task(
            id=uuid4(),
            title="   ",  # Whitespace only - currently allowed
            description="Valid description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert task.title == "   "

    def test_task_list_with_empty_name_validation(self):
        """Test task list creation with empty name should raise validation error."""
        with pytest.raises(ValueError):
            TaskList(
                id=uuid4(),
                name="",  # Empty name
                description="Valid description",
                owner_id=uuid4(),
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_user_with_invalid_email_formats(self):
        """Test user creation with various invalid email formats."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user..double.dot@example.com",
            "user@.com",
            "user@com",
            "",
            "   ",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError):
                User(
                    id=uuid4(),
                    email=invalid_email,
                    username="validuser",
                    full_name="Valid User",
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

    def test_user_with_empty_username_validation(self):
        """Test user creation with empty username should raise validation error."""
        with pytest.raises(ValueError):
            User(
                id=uuid4(),
                email="valid@example.com",
                username="",  # Empty username
                full_name="Valid User",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_task_due_date_edge_cases(self):
        """Test task due date edge cases."""
        now = datetime.now(timezone.utc)

        # Task due exactly now
        task_due_now = Task(
            id=uuid4(),
            title="Due Now Task",
            description="Task due exactly now",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=now,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # Should be considered overdue (due time has passed)
        assert task_due_now.is_overdue is True

        # Task due 1 second ago
        task_due_past = Task(
            id=uuid4(),
            title="Due Past Task",
            description="Task due 1 second ago",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=now - timedelta(seconds=1),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert task_due_past.is_overdue is True

        # Task due 1 second in future
        task_due_future = Task(
            id=uuid4(),
            title="Due Future Task",
            description="Task due 1 second in future",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=now + timedelta(seconds=1),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert task_due_future.is_overdue is False

    def test_task_priority_boundary_values(self):
        """Test task priority with all valid enum values."""
        priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]

        for priority in priorities:
            task = Task(
                id=uuid4(),
                title=f"Task with {priority.value} priority",
                description="Testing priority values",
                status=TaskStatus.PENDING,
                priority=priority,
                task_list_id=uuid4(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            assert task.priority == priority

    def test_task_status_boundary_values(self):
        """Test task status with all valid enum values."""
        statuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]

        for status in statuses:
            task = Task(
                id=uuid4(),
                title=f"Task with {status.value} status",
                description="Testing status values",
                status=status,
                priority=TaskPriority.MEDIUM,
                task_list_id=uuid4(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            assert task.status == status

    def test_task_update_details_with_none_values(self):
        """Test updating task details with None values (should keep original)."""
        original_task = Task(
            id=uuid4(),
            title="Original Title",
            description="Original Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Update with None values should keep original
        updated_task = original_task.update_details(title=None, description=None)

        assert updated_task.title == "Original Title"
        assert updated_task.description == "Original Description"

    def test_task_list_update_details_with_none_values(self):
        """Test updating task list details with None values."""
        original_list = TaskList(
            id=uuid4(),
            name="Original Name",
            description="Original Description",
            owner_id=uuid4(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Update with None values should keep original
        updated_list = original_list.update_details(name=None, description=None)

        assert updated_list.name == "Original Name"
        assert updated_list.description == "Original Description"

    def test_user_update_profile_with_partial_data(self):
        """Test updating user profile with partial data."""
        original_user = User(
            id=uuid4(),
            email="original@example.com",
            username="originaluser",
            full_name="Original User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Update only full name
        updated_user = original_user.update_profile(full_name="Updated User")

        assert updated_user.full_name == "Updated User"
        assert updated_user.email == "original@example.com"  # Should remain unchanged
        assert updated_user.username == "originaluser"  # Should remain unchanged

        # Update only email
        updated_user_2 = original_user.update_profile(email="updated@example.com")

        assert updated_user_2.email == "updated@example.com"
        assert updated_user_2.full_name == "Original User"  # Should remain unchanged
        assert updated_user_2.username == "originaluser"  # Should remain unchanged

    def test_task_completed_at_consistency(self):
        """Test that completed_at is set correctly when marking as completed."""
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Initially no completed_at
        assert task.completed_at is None

        # Mark as completed
        completed_task = task.mark_as_completed()

        # Should have completed_at set
        assert completed_task.completed_at is not None
        assert completed_task.status == TaskStatus.COMPLETED

        # Mark as pending again
        reopened_task = completed_task.mark_as_pending()

        # completed_at should be cleared
        assert reopened_task.completed_at is None
        assert reopened_task.status == TaskStatus.PENDING
