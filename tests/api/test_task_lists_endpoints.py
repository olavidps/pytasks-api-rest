"""Tests for task list endpoints using mocked dependencies.

These tests mock all dependencies to avoid database connections,
focusing purely on HTTP behavior and response validation.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_create_task_list_use_case,
    get_delete_task_list_use_case,
    get_get_tasks_use_case,
    get_task_list_use_case,
    get_update_task_list_use_case,
)
from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.main import app

# Create global mock instances
mock_create_task_list_use_case = AsyncMock()
mock_get_task_list_use_case = AsyncMock()
mock_get_tasks_use_case = AsyncMock()
mock_update_task_list_use_case = AsyncMock()
mock_delete_task_list_use_case = AsyncMock()


# Mock dependency functions
def get_mock_create_task_list_use_case():
    """Return mock create task list use case."""
    return mock_create_task_list_use_case


def get_mock_get_task_list_use_case():
    """Return mock get task list use case."""
    return mock_get_task_list_use_case


def get_mock_get_tasks_use_case():
    """Return mock get tasks use case."""
    return mock_get_tasks_use_case


def get_mock_update_task_list_use_case():
    """Return mock update task list use case."""
    return mock_update_task_list_use_case


def get_mock_delete_task_list_use_case():
    """Return mock delete task list use case."""
    return mock_delete_task_list_use_case


# Setup dependency overrides with proper cleanup
@pytest.fixture(autouse=True)
def setup_task_list_mocks():
    """Set up task list mocks for each test."""
    # Reset all mocks before each test
    mock_create_task_list_use_case.reset_mock()
    mock_get_task_list_use_case.reset_mock()
    mock_get_tasks_use_case.reset_mock()
    mock_update_task_list_use_case.reset_mock()
    mock_delete_task_list_use_case.reset_mock()

    # Override dependencies
    app.dependency_overrides[get_create_task_list_use_case] = (
        get_mock_create_task_list_use_case
    )
    app.dependency_overrides[get_task_list_use_case] = get_mock_get_task_list_use_case
    app.dependency_overrides[get_get_tasks_use_case] = get_mock_get_tasks_use_case
    app.dependency_overrides[get_update_task_list_use_case] = (
        get_mock_update_task_list_use_case
    )
    app.dependency_overrides[get_delete_task_list_use_case] = (
        get_mock_delete_task_list_use_case
    )

    yield

    # Cleanup after each test
    if get_create_task_list_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_create_task_list_use_case]
    if get_task_list_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_task_list_use_case]
    if get_get_tasks_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_get_tasks_use_case]
    if get_update_task_list_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_update_task_list_use_case]
    if get_delete_task_list_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_delete_task_list_use_case]


class TestCreateTaskListEndpoint:
    """Test cases for POST /api/v1/task-lists endpoint using mocks."""

    def test_create_task_list_success(self):
        """Test successful task list creation."""
        # Arrange
        task_list_data = {
            "name": "New Task List",
            "description": "Task list description",
        }

        created_task_list = TaskList(
            id=uuid.uuid4(),
            name=task_list_data["name"],
            description=task_list_data["description"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_create_task_list_use_case.execute.return_value = created_task_list

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/task-lists/", json=task_list_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == task_list_data["name"]
        assert response_data["description"] == task_list_data["description"]
        assert response_data["is_active"] is True
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_create_task_list_minimal_data(self):
        """Test creating task list with minimal required data."""
        # Arrange
        task_list_data = {"name": "Minimal Task List"}

        created_task_list = TaskList(
            id=uuid.uuid4(),
            name=task_list_data["name"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_create_task_list_use_case.execute.return_value = created_task_list

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/task-lists/", json=task_list_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == task_list_data["name"]
        assert response_data["description"] is None

    def test_create_task_list_invalid_data(self):
        """Test creating task list with invalid data returns 422."""
        # Arrange
        task_list_data = {
            "name": "",  # Empty name should fail validation
        }

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/task-lists/", json=task_list_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTaskListEndpoint:
    """Test cases for GET /api/v1/task-lists/{task_list_id} endpoint using mocks."""

    def test_get_task_list_success(self):
        """Test successful task list retrieval."""
        # Arrange
        task_list_id = uuid.uuid4()

        # Create a mock response that matches TaskListWithStats schema
        mock_response = {
            "id": task_list_id,
            "name": "Test Task List",
            "description": "Test description",
            "owner_id": None,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "completion_percentage": 0,
        }

        mock_get_task_list_use_case.get_by_id.return_value = mock_response

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/task-lists/{task_list_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == str(task_list_id)
        assert response_data["name"] == "Test Task List"
        assert response_data["description"] == "Test description"
        assert response_data["is_active"] is True

    def test_get_task_list_not_found(self):
        """Test getting non-existent task list returns 404."""
        # Arrange
        task_list_id = uuid.uuid4()
        mock_get_task_list_use_case.get_by_id.side_effect = TaskListNotFoundError(
            task_list_id
        )

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/task-lists/{task_list_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "TaskList" in response.json()["detail"]
        assert str(task_list_id) in response.json()["detail"]

    def test_get_task_list_invalid_uuid(self):
        """Test getting task list with invalid UUID returns 422."""
        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/task-lists/invalid-uuid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTaskListsEndpoint:
    """Test cases for GET /api/v1/task-lists endpoint using mocks."""

    def test_get_task_lists_success(self):
        """Test successful task lists retrieval with pagination."""
        # Arrange
        task_lists = [
            TaskList(
                id=uuid.uuid4(),
                name=f"Task List {i}",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(3)
        ]

        mock_get_task_list_use_case.get_paginated.return_value = {
            "items": [
                {
                    "id": str(task_list.id),
                    "name": task_list.name,
                    "description": task_list.description,
                    "owner_id": task_list.owner_id,
                    "is_active": task_list.is_active,
                    "created_at": task_list.created_at.isoformat(),
                    "updated_at": task_list.updated_at.isoformat(),
                }
                for task_list in task_lists
            ],
            "page": 1,
            "size": 20,
            "total": 3,
            "pages": 1,
        }

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/task-lists/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "items" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert "total" in response_data
        assert "pages" in response_data
        assert len(response_data["items"]) == 3
        assert response_data["total"] == 3

    def test_get_task_lists_with_pagination(self):
        """Test getting task lists with pagination parameters."""
        # Arrange
        mock_get_task_list_use_case.get_paginated.return_value = {
            "items": [],
            "page": 2,
            "size": 10,
            "total": 0,
            "pages": 0,
        }

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/task-lists/?page=2&size=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["page"] == 2
        assert response_data["size"] == 10
        assert response_data["total"] == 0


class TestGetTaskListTasksEndpoint:
    """Test cases for GET /api/v1/task-lists/{task_list_id}/tasks endpoint using mocks."""

    def test_get_task_list_tasks_success(self):
        """Test successful retrieval of tasks from a task list."""
        # Arrange
        task_list_id = uuid.uuid4()

        # Task list data for reference (not used in mock setup)
        # task_list = TaskList(
        #     id=task_list_id,
        #     name="Test Task List",
        #     is_active=True,
        #     created_at=datetime.now(),
        #     updated_at=datetime.now(),
        # )

        tasks = [
            Task(
                id=uuid.uuid4(),
                title=f"Task {i}",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                task_list_id=task_list_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(2)
        ]

        from types import SimpleNamespace

        task_list_stats = SimpleNamespace(
            id=task_list_id,
            name="Test Task List",
            description=None,
            owner_id=None,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_tasks=2,
            completed_tasks=0,
            pending_tasks=2,
            in_progress_tasks=0,
            completion_percentage=0,
        )
        mock_get_task_list_use_case.get_by_id.return_value = task_list_stats
        mock_get_tasks_use_case.execute.return_value = (tasks, 2)

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/task-lists/{task_list_id}/tasks")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == str(task_list_id)
        assert response_data["name"] == "Test Task List"
        assert "tasks" in response_data
        assert len(response_data["tasks"]) == 2
        assert "total_tasks" in response_data
        assert "completed_tasks" in response_data
        assert "pending_tasks" in response_data
        assert "in_progress_tasks" in response_data
        assert "completion_percentage" in response_data

    def test_get_task_list_tasks_with_status_filter(self):
        """Test retrieving tasks from a task list with status filter."""
        # Arrange
        task_list_id = uuid.uuid4()

        completed_tasks = [
            Task(
                id=uuid.uuid4(),
                title="Completed Task",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.COMPLETED,
                task_list_id=task_list_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                completed_at=datetime.now(),
            )
        ]

        from types import SimpleNamespace

        task_list_stats = SimpleNamespace(
            id=task_list_id,
            name="Test Task List",
            description=None,
            owner_id=None,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_tasks=1,
            completed_tasks=1,
            pending_tasks=0,
            in_progress_tasks=0,
            completion_percentage=100,
        )
        mock_get_task_list_use_case.get_by_id.return_value = task_list_stats
        mock_get_tasks_use_case.execute.return_value = (completed_tasks, 1)

        # Act
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/task-lists/{task_list_id}/tasks?status=completed"
            )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["tasks"]) == 1
        assert response_data["tasks"][0]["status"] == "completed"

    def test_get_task_list_tasks_not_found(self):
        """Test getting tasks from non-existent task list returns 404."""
        # Arrange
        task_list_id = uuid.uuid4()
        mock_get_task_list_use_case.get_by_id.side_effect = TaskListNotFoundError(
            task_list_id
        )

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/task-lists/{task_list_id}/tasks")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTaskListEndpoint:
    """Test cases for PUT /api/v1/task-lists/{task_list_id} endpoint using mocks."""

    def test_update_task_list_success(self):
        """Test successful task list update."""
        # Arrange
        task_list_id = uuid.uuid4()
        update_data = {
            "name": "Updated Task List",
            "description": "Updated description",
        }

        updated_task_list = TaskList(
            id=task_list_id,
            name=update_data["name"],
            description=update_data["description"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_update_task_list_use_case.execute.return_value = updated_task_list

        # Act
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/task-lists/{task_list_id}", json=update_data
            )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == update_data["name"]
        assert response_data["description"] == update_data["description"]

    def test_update_task_list_not_found(self):
        """Test updating non-existent task list returns 404."""
        # Arrange
        task_list_id = uuid.uuid4()
        update_data = {"name": "Updated Name"}
        mock_update_task_list_use_case.execute.side_effect = TaskListNotFoundError(
            task_list_id
        )

        # Act
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/task-lists/{task_list_id}", json=update_data
            )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_list_invalid_data(self):
        """Test updating task list with invalid data returns 422."""
        # Arrange
        task_list_id = uuid.uuid4()
        update_data = {"name": ""}  # Empty name should fail validation

        # Act
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/task-lists/{task_list_id}", json=update_data
            )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteTaskListEndpoint:
    """Test cases for DELETE /api/v1/task-lists/{task_list_id} endpoint using mocks."""

    def test_delete_task_list_success(self):
        """Test successful task list deletion."""
        # Arrange
        task_list_id = uuid.uuid4()
        mock_delete_task_list_use_case.execute.return_value = None

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/task-lists/{task_list_id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_task_list_not_found(self):
        """Test deleting non-existent task list returns 404."""
        # Arrange
        task_list_id = uuid.uuid4()
        mock_delete_task_list_use_case.execute.side_effect = TaskListNotFoundError(
            task_list_id
        )

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/task-lists/{task_list_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "TaskList" in response.json()["detail"]
        assert str(task_list_id) in response.json()["detail"]
