"""Extended tests for TaskList domain model."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.domain.models.task_list import TaskList


class TestTaskListModelExtended:
    """Extended test cases for TaskList model."""

    def test_task_list_update_details_all_fields(self):
        """Test updating all task list details."""
        task_list = TaskList(name="Original List", description="Original description")

        updated_list = task_list.update_details(
            name="Updated List", description="Updated description"
        )

        assert updated_list.name == "Updated List"
        assert updated_list.description == "Updated description"
        assert updated_list.updated_at > task_list.updated_at
        assert updated_list.id == task_list.id

    def test_task_list_update_details_name_only(self):
        """Test updating only the name."""
        task_list = TaskList(name="Original List", description="Original description")

        updated_list = task_list.update_details(name="Updated List")

        assert updated_list.name == "Updated List"
        assert updated_list.description == task_list.description  # unchanged
        assert updated_list.updated_at > task_list.updated_at

    def test_task_list_update_details_description_only(self):
        """Test updating only the description."""
        task_list = TaskList(name="Original List", description="Original description")

        updated_list = task_list.update_details(description="Updated description")

        assert updated_list.name == "Original List"  # unchanged
        assert updated_list.description == "Updated description"
        assert updated_list.updated_at > task_list.updated_at

    def test_task_list_update_details_no_changes(self):
        """Test update details with no changes."""
        task_list = TaskList(name="Original List", description="Original description")

        updated_list = task_list.update_details()

        assert updated_list.name == task_list.name
        assert updated_list.description == task_list.description
        assert updated_list.updated_at > task_list.updated_at

    def test_task_list_deactivate(self):
        """Test task list deactivation."""
        task_list = TaskList(name="Test List", is_active=True)

        deactivated_list = task_list.deactivate()

        assert deactivated_list.is_active is False
        assert deactivated_list.updated_at > task_list.updated_at
        assert deactivated_list.id == task_list.id
        assert deactivated_list.name == task_list.name

    def test_task_list_activate(self):
        """Test task list activation."""
        task_list = TaskList(name="Test List", is_active=False)

        activated_list = task_list.activate()

        assert activated_list.is_active is True
        assert activated_list.updated_at > task_list.updated_at
        assert activated_list.id == task_list.id
        assert activated_list.name == task_list.name

    def test_task_list_validation_errors(self):
        """Test task list validation errors."""
        # Test name too short (empty)
        with pytest.raises(ValidationError):
            TaskList(name="")

        # Test name too long
        with pytest.raises(ValidationError):
            TaskList(name="a" * 101)  # more than 100 characters

        # Test description too long
        with pytest.raises(ValidationError):
            TaskList(
                name="Valid Name", description="a" * 501  # more than 500 characters
            )

    def test_task_list_immutability(self):
        """Test that TaskList model is immutable."""
        task_list = TaskList(name="Test List")

        # Should not be able to modify attributes directly
        with pytest.raises(ValidationError):
            task_list.name = "New Name"

        with pytest.raises(ValidationError):
            task_list.is_active = False

    def test_task_list_id_generation(self):
        """Test that task list ID is automatically generated."""
        list1 = TaskList(name="List 1")
        list2 = TaskList(name="List 2")

        assert isinstance(list1.id, UUID)
        assert isinstance(list2.id, UUID)
        assert list1.id != list2.id

    def test_task_list_default_values(self):
        """Test task list default values."""
        task_list = TaskList(name="Test List")

        assert task_list.description is None
        assert task_list.owner_id is None
        assert task_list.is_active is True
        assert task_list.tasks == []
        assert isinstance(task_list.created_at, datetime)
        assert isinstance(task_list.updated_at, datetime)
        assert task_list.created_at.tzinfo == timezone.utc
        assert task_list.updated_at.tzinfo == timezone.utc

    def test_task_list_with_owner(self):
        """Test task list creation with owner."""
        owner_id = uuid4()
        task_list = TaskList(name="Test List", owner_id=owner_id)

        assert task_list.owner_id == owner_id
        assert task_list.name == "Test List"

    def test_task_list_with_description(self):
        """Test task list creation with description."""
        task_list = TaskList(name="Test List", description="This is a test list")

        assert task_list.description == "This is a test list"
        assert task_list.name == "Test List"

    def test_task_list_update_details_no_description_change(self):
        """Test that passing None for description doesn't change it."""
        task_list = TaskList(name="Test List", description="Original description")

        updated_list = task_list.update_details(description=None)

        assert updated_list.description == "Original description"
        assert updated_list.name == "Test List"
        assert updated_list.updated_at > task_list.updated_at

    def test_task_list_update_details_empty_description(self):
        """Test setting description to empty string."""
        task_list = TaskList(name="Test List", description="Original description")

        updated_list = task_list.update_details(description="")

        assert updated_list.description == ""
        assert updated_list.name == "Test List"
        assert updated_list.updated_at > task_list.updated_at
