"""Unit tests for TaskList domain model."""

from datetime import datetime
from uuid import uuid4

from app.domain.models.task_list import TaskList


class TestTaskList:
    """Unit tests for TaskList domain entity."""

    def test_create_task_list_success(self):
        """Test successful task list creation with valid data."""
        task_list_id = uuid4()
        owner_id = uuid4()
        name = "My Task List"
        description = "A list of tasks"

        task_list = TaskList(
            id=task_list_id,
            name=name,
            description=description,
            owner_id=owner_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task_list.id == task_list_id
        assert task_list.name == name
        assert task_list.description == description
        assert task_list.owner_id == owner_id

    def test_create_task_list_without_description(self):
        """Test task list creation without description."""
        task_list_id = uuid4()
        owner_id = uuid4()
        name = "My Task List"

        task_list = TaskList(
            id=task_list_id,
            name=name,
            description=None,
            owner_id=owner_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task_list.id == task_list_id
        assert task_list.name == name
        assert task_list.description is None
        assert task_list.owner_id == owner_id

    def test_task_list_update_name(self):
        """Test updating task list name."""
        task_list = TaskList(
            id=uuid4(),
            name="Original Name",
            description="A list of tasks",
            owner_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        new_name = "Updated Name"
        updated_task_list = task_list.update_details(name=new_name)

        assert updated_task_list.name == new_name
        assert updated_task_list.id == task_list.id
        assert updated_task_list.owner_id == task_list.owner_id
        assert updated_task_list.description == task_list.description

    def test_task_list_update_description(self):
        """Test updating task list description."""
        task_list = TaskList(
            id=uuid4(),
            name="My Task List",
            description="Original description",
            owner_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        new_description = "Updated description"
        updated_task_list = task_list.update_details(description=new_description)

        assert updated_task_list.description == new_description
        assert updated_task_list.id == task_list.id
        assert updated_task_list.name == task_list.name
        assert updated_task_list.owner_id == task_list.owner_id

    def test_task_list_clear_description(self):
        """Test clearing task list description."""
        task_list = TaskList(
            id=uuid4(),
            name="My Task List",
            description="Some description",
            owner_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Clear description by setting it to empty string
        updated_task_list = task_list.update_details(description="")

        assert updated_task_list.description == ""
        assert updated_task_list.id == task_list.id
        assert updated_task_list.name == task_list.name
        assert updated_task_list.owner_id == task_list.owner_id

    def test_task_list_immutability(self):
        """Test that task list is immutable."""
        original_name = "Original Name"
        task_list = TaskList(
            id=uuid4(),
            name=original_name,
            description="A list of tasks",
            owner_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Update should return new instance
        updated_task_list = task_list.update_details(name="New Name")

        # Original should remain unchanged
        assert task_list.name == original_name
        assert updated_task_list.name == "New Name"
        assert task_list is not updated_task_list
