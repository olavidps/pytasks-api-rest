"""Tests for API schemas."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api.schemas.common_schemas import PaginatedResponse
from app.api.schemas.task_list_schemas import (
    TaskListCreate,
    TaskListResponse,
    TaskListUpdate,
)
from app.api.schemas.task_schemas import (
    TaskCreate,
    TaskFilterParams,
    TaskResponse,
    TaskUpdate,
)
from app.api.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.domain.models.task import TaskPriority, TaskStatus


class TestCommonSchemas:
    """Test cases for common schemas."""

    def test_paginated_response_create_success(self):
        """Test successful creation of paginated response."""
        items = ["item1", "item2", "item3"]
        total = 10
        page = 1
        size = 3

        paginated = PaginatedResponse.create(
            items=items, total=total, page=page, size=size
        )

        assert paginated.items == items
        assert paginated.total == total
        assert paginated.page == page
        assert paginated.size == size
        assert paginated.pages == 4  # ceil(10/3) = 4

    def test_paginated_response_create_empty(self):
        """Test creation of paginated response with empty items."""
        items = []
        total = 0
        page = 1
        size = 10

        paginated = PaginatedResponse.create(
            items=items, total=total, page=page, size=size
        )

        assert paginated.items == []
        assert paginated.total == 0
        assert paginated.page == 1
        assert paginated.size == 10
        assert paginated.pages == 0

    def test_paginated_response_create_single_page(self):
        """Test creation of paginated response with single page."""
        items = ["item1", "item2"]
        total = 2
        page = 1
        size = 10

        paginated = PaginatedResponse.create(
            items=items, total=total, page=page, size=size
        )

        assert paginated.pages == 1


class TestUserSchemas:
    """Test cases for user schemas."""

    def test_user_create_valid(self):
        """Test valid user creation schema."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
        }

        user_create = UserCreate(**user_data)

        assert user_create.email == user_data["email"]
        assert user_create.username == user_data["username"]
        assert user_create.full_name == user_data["full_name"]
        assert user_create.is_active == user_data["is_active"]

    def test_user_create_minimal(self):
        """Test user creation with minimal required fields."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
        }

        user_create = UserCreate(**user_data)

        assert user_create.email == user_data["email"]
        assert user_create.username == user_data["username"]
        assert user_create.full_name == user_data["full_name"]
        assert user_create.is_active is True  # Default value

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "email" in str(exc_info.value)

    def test_user_create_missing_required_fields(self):
        """Test user creation with missing required fields."""
        user_data = {
            "email": "test@example.com"
            # Missing username and full_name
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = str(exc_info.value)
        assert "username" in errors
        assert "full_name" in errors

    def test_user_update_partial(self):
        """Test user update schema with partial data."""
        update_data = {"full_name": "Updated Name", "is_active": False}

        user_update = UserUpdate(**update_data)

        assert user_update.full_name == update_data["full_name"]
        assert user_update.is_active == update_data["is_active"]
        assert user_update.email is None
        assert user_update.username is None

    def test_user_update_empty(self):
        """Test user update schema with no data."""
        user_update = UserUpdate()

        assert user_update.email is None
        assert user_update.username is None
        assert user_update.full_name is None
        assert user_update.is_active is None

    def test_user_response_from_domain(self, sample_user):
        """Test user response schema creation from domain model."""
        user_response = UserResponse.model_validate(sample_user)

        assert str(user_response.id) == str(sample_user.id)
        assert user_response.email == sample_user.email
        assert user_response.username == sample_user.username
        assert user_response.full_name == sample_user.full_name
        assert user_response.is_active == sample_user.is_active
        assert user_response.created_at == sample_user.created_at
        assert user_response.updated_at == sample_user.updated_at


class TestTaskListSchemas:
    """Test cases for task list schemas."""

    def test_task_list_create_valid(self):
        """Test valid task list creation schema."""
        owner_id = uuid4()
        task_list_data = {
            "name": "My Task List",
            "description": "A list for my tasks",
            "owner_id": owner_id,
        }

        task_list_create = TaskListCreate(**task_list_data)

        assert task_list_create.name == task_list_data["name"]
        assert task_list_create.description == task_list_data["description"]
        assert task_list_create.owner_id == task_list_data["owner_id"]

    def test_task_list_create_minimal(self):
        """Test task list creation with minimal required fields."""
        owner_id = uuid4()
        task_list_data = {"name": "My Task List", "owner_id": owner_id}

        task_list_create = TaskListCreate(**task_list_data)

        assert task_list_create.name == task_list_data["name"]
        assert task_list_create.owner_id == task_list_data["owner_id"]
        assert task_list_create.description is None

    def test_task_list_create_missing_required_fields(self):
        """Test task list creation with missing required fields."""
        task_list_data = {
            "name": "My Task List"
            # Missing owner_id
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskListCreate(**task_list_data)

        assert "owner_id" in str(exc_info.value)

    def test_task_list_update_partial(self):
        """Test task list update schema with partial data."""
        update_data = {"name": "Updated Task List", "is_active": False}

        task_list_update = TaskListUpdate(**update_data)

        assert task_list_update.name == update_data["name"]
        assert task_list_update.is_active == update_data["is_active"]
        assert task_list_update.description is None

    def test_task_list_response_from_domain(self, sample_task_list):
        """Test task list response schema creation from domain model."""
        task_list_response = TaskListResponse.model_validate(sample_task_list)

        assert str(task_list_response.id) == str(sample_task_list.id)
        assert task_list_response.name == sample_task_list.name
        assert task_list_response.description == sample_task_list.description
        assert str(task_list_response.owner_id) == str(sample_task_list.owner_id)
        assert task_list_response.is_active == sample_task_list.is_active
        assert task_list_response.created_at == sample_task_list.created_at
        assert task_list_response.updated_at == sample_task_list.updated_at

    def test_paginated_task_list_response_type(self):
        """Test that PaginatedTaskListResponse is properly typed."""
        # This test ensures the type alias works correctly
        task_list_responses = []
        paginated = PaginatedResponse[TaskListResponse].create(
            items=task_list_responses, total=0, page=1, size=10
        )

        assert isinstance(paginated, PaginatedResponse)
        assert paginated.items == []


class TestTaskSchemas:
    """Test cases for task schemas."""

    def test_task_create_valid(self):
        """Test valid task creation schema."""
        task_list_id = uuid4()
        assigned_to_id = uuid4()
        due_date = datetime.now()

        task_data = {
            "title": "New Task",
            "description": "Task description",
            "status": TaskStatus.PENDING,
            "priority": TaskPriority.HIGH,
            "task_list_id": task_list_id,
            "assigned_to_id": assigned_to_id,
            "due_date": due_date,
        }

        task_create = TaskCreate(**task_data)

        assert task_create.title == task_data["title"]
        assert task_create.description == task_data["description"]
        assert task_create.status == task_data["status"]
        assert task_create.priority == task_data["priority"]
        assert task_create.task_list_id == task_data["task_list_id"]
        assert task_create.assigned_to_id == task_data["assigned_to_id"]
        assert task_create.due_date == task_data["due_date"]

    def test_task_create_minimal(self):
        """Test task creation with minimal required fields."""
        task_list_id = uuid4()
        task_data = {"title": "Minimal Task", "task_list_id": task_list_id}

        task_create = TaskCreate(**task_data)

        assert task_create.title == task_data["title"]
        assert task_create.task_list_id == task_data["task_list_id"]
        assert task_create.description is None
        assert task_create.status == TaskStatus.PENDING  # Default
        assert task_create.priority == TaskPriority.MEDIUM  # Default
        assert task_create.assigned_to_id is None
        assert task_create.due_date is None

    def test_task_create_missing_required_fields(self):
        """Test task creation with missing required fields."""
        task_data = {
            "title": "New Task"
            # Missing task_list_id
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**task_data)

        assert "task_list_id" in str(exc_info.value)

    def test_task_create_invalid_status(self):
        """Test task creation with invalid status."""
        task_list_id = uuid4()
        task_data = {
            "title": "New Task",
            "task_list_id": task_list_id,
            "status": "invalid_status",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**task_data)

        assert "status" in str(exc_info.value)

    def test_task_create_invalid_priority(self):
        """Test task creation with invalid priority."""
        task_list_id = uuid4()
        task_data = {
            "title": "New Task",
            "task_list_id": task_list_id,
            "priority": "invalid_priority",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**task_data)

        assert "priority" in str(exc_info.value)

    def test_task_update_partial(self):
        """Test task update schema with partial data."""
        update_data = {"title": "Updated Task", "status": TaskStatus.COMPLETED}

        task_update = TaskUpdate(**update_data)

        assert task_update.title == update_data["title"]
        assert task_update.status == update_data["status"]
        assert task_update.description is None
        assert task_update.priority is None
        assert task_update.assigned_to_id is None
        assert task_update.due_date is None

    def test_task_response_from_domain(self, sample_task):
        """Test task response schema creation from domain model."""
        task_response = TaskResponse.model_validate(sample_task)

        assert str(task_response.id) == str(sample_task.id)
        assert task_response.title == sample_task.title
        assert task_response.description == sample_task.description
        assert task_response.status == sample_task.status
        assert task_response.priority == sample_task.priority
        assert str(task_response.task_list_id) == str(sample_task.task_list_id)
        assert str(task_response.assigned_to_id) == str(sample_task.assigned_user_id)
        assert task_response.due_date == sample_task.due_date
        assert task_response.created_at == sample_task.created_at
        assert task_response.updated_at == sample_task.updated_at

    def test_task_filter_params_valid(self):
        """Test valid task filter parameters."""
        task_list_id = uuid4()
        assigned_to_id = uuid4()
        due_date_from = datetime.now()
        due_date_to = datetime.now()

        filter_params = TaskFilterParams(
            task_list_id=task_list_id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            assigned_to_id=assigned_to_id,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
        )

        assert filter_params.task_list_id == task_list_id
        assert filter_params.status == TaskStatus.PENDING
        assert filter_params.priority == TaskPriority.HIGH
        assert filter_params.assigned_to_id == assigned_to_id
        assert filter_params.due_date_from == due_date_from
        assert filter_params.due_date_to == due_date_to

    def test_task_filter_params_empty(self):
        """Test task filter parameters with no filters."""
        filter_params = TaskFilterParams()

        assert filter_params.task_list_id is None
        assert filter_params.status is None
        assert filter_params.priority is None
        assert filter_params.assigned_to_id is None
        assert filter_params.due_date_from is None
        assert filter_params.due_date_to is None

    def test_paginated_task_response_type(self):
        """Test that PaginatedTaskResponse is properly typed."""
        # This test ensures the type alias works correctly
        task_responses = []
        paginated = PaginatedResponse[TaskResponse].create(
            items=task_responses, total=0, page=1, size=10
        )

        assert isinstance(paginated, PaginatedResponse)
        assert paginated.items == []
