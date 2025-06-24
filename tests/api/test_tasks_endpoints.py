"""Tests for task endpoints using mocked dependencies.

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
    get_create_task_use_case,
    get_delete_task_use_case,
    get_get_task_use_case,
    get_get_tasks_use_case,
    get_update_task_priority_use_case,
    get_update_task_status_use_case,
    get_update_task_use_case,
)
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.main import app

# Create global mock instances
mock_create_task_use_case = AsyncMock()
mock_get_task_use_case = AsyncMock()
mock_get_tasks_use_case = AsyncMock()
mock_update_task_use_case = AsyncMock()
mock_update_task_priority_use_case = AsyncMock()
mock_update_task_status_use_case = AsyncMock()
mock_delete_task_use_case = AsyncMock()


# Mock dependency functions
def get_mock_create_task_use_case():
    """Return mock create task use case."""
    return mock_create_task_use_case


def get_mock_get_task_use_case():
    """Return mock get task use case."""
    return mock_get_task_use_case


def get_mock_get_tasks_use_case():
    """Return mock get tasks use case."""
    return mock_get_tasks_use_case


def get_mock_update_task_use_case():
    """Return mock update task use case."""
    return mock_update_task_use_case


def get_mock_update_task_priority_use_case():
    """Return mock update task priority use case."""
    return mock_update_task_priority_use_case


def get_mock_update_task_status_use_case():
    """Return mock update task status use case."""
    return mock_update_task_status_use_case


def get_mock_delete_task_use_case():
    """Return mock delete task use case."""
    return mock_delete_task_use_case


# Setup dependency overrides with proper cleanup
@pytest.fixture(autouse=True)
def setup_task_mocks():
    """Set up task mocks for each test."""
    # Reset all mocks before each test
    mock_create_task_use_case.reset_mock()
    mock_get_task_use_case.reset_mock()
    mock_get_tasks_use_case.reset_mock()
    mock_update_task_use_case.reset_mock()
    mock_update_task_priority_use_case.reset_mock()
    mock_update_task_status_use_case.reset_mock()
    mock_delete_task_use_case.reset_mock()

    # Override dependencies
    app.dependency_overrides[get_create_task_use_case] = get_mock_create_task_use_case
    app.dependency_overrides[get_get_task_use_case] = get_mock_get_task_use_case
    app.dependency_overrides[get_get_tasks_use_case] = get_mock_get_tasks_use_case
    app.dependency_overrides[get_update_task_use_case] = get_mock_update_task_use_case
    app.dependency_overrides[get_update_task_priority_use_case] = (
        get_mock_update_task_priority_use_case
    )
    app.dependency_overrides[get_update_task_status_use_case] = (
        get_mock_update_task_status_use_case
    )
    app.dependency_overrides[get_delete_task_use_case] = get_mock_delete_task_use_case

    yield

    # Cleanup after each test
    if get_create_task_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_create_task_use_case]
    if get_get_task_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_get_task_use_case]
    if get_get_tasks_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_get_tasks_use_case]
    if get_update_task_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_update_task_use_case]
    if get_update_task_priority_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_update_task_priority_use_case]
    if get_update_task_status_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_update_task_status_use_case]
    if get_delete_task_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_delete_task_use_case]


class TestCreateTaskEndpoint:
    """Test cases for POST /api/v1/tasks endpoint using mocks."""

    def test_create_task_success(self):
        """Test successful task creation."""
        # Arrange
        task_list_id = uuid.uuid4()
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high",
            "task_list_id": str(task_list_id),
        }

        created_task = Task(
            id=uuid.uuid4(),
            title=task_data["title"],
            description=task_data["description"],
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_create_task_use_case.execute.return_value = created_task

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/tasks/", json=task_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["title"] == task_data["title"]
        assert response_data["description"] == task_data["description"]
        assert response_data["priority"] == task_data["priority"]
        assert response_data["status"] == "pending"
        assert response_data["task_list_id"] == str(task_list_id)
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_create_task_invalid_task_list(self):
        """Test creating task with invalid task list ID raises 404."""
        # Arrange
        task_data = {
            "title": "New Task",
            "task_list_id": str(uuid.uuid4()),
        }

        mock_create_task_use_case.execute.side_effect = TaskListNotFoundError(
            uuid.UUID(task_data["task_list_id"])
        )

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/tasks/", json=task_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "TaskList" in response.json()["detail"]
        assert "not found" in response.json()["detail"]

    def test_create_task_invalid_data(self):
        """Test creating task with invalid data returns 422."""
        # Arrange
        task_data = {
            "title": "",  # Empty title should fail validation
            "task_list_id": str(uuid.uuid4()),
        }

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/tasks/", json=task_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTaskEndpoint:
    """Test cases for GET /api/v1/tasks/{task_id} endpoint using mocks."""

    def test_get_task_success(self):
        """Test successful task retrieval."""
        # Arrange
        task_id = uuid.uuid4()
        task_list_id = uuid.uuid4()

        # Create a mock response that matches TaskWithRelations schema
        task_with_relations = {
            "id": str(task_id),
            "title": "Test Task",
            "description": "Test description",
            "priority": "medium",
            "status": "pending",
            "task_list_id": str(task_list_id),
            "assigned_user_id": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "due_date": None,
            "completed_at": None,
            "task_list": {"id": str(task_list_id), "name": "Test Task List"},
            "assigned_user": None,
        }

        mock_get_task_use_case.execute.return_value = task_with_relations

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == str(task_id)
        assert response_data["title"] == "Test Task"
        assert response_data["task_list"]["name"] == "Test Task List"
        assert response_data["description"] == "Test description"
        assert response_data["priority"] == "medium"
        assert response_data["status"] == "pending"
        assert response_data["task_list_id"] == str(task_list_id)

    def test_get_task_not_found(self):
        """Test getting non-existent task returns 404."""
        # Arrange
        task_id = uuid.uuid4()
        mock_get_task_use_case.execute.side_effect = TaskNotFoundError(task_id)

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task" in response.json()["detail"]
        assert str(task_id) in response.json()["detail"]

    def test_get_task_invalid_uuid(self):
        """Test getting task with invalid UUID returns 422."""
        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/tasks/invalid-uuid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTasksEndpoint:
    """Test cases for GET /api/v1/tasks endpoint using mocks."""

    def test_get_tasks_success(self):
        """Test successful tasks retrieval with pagination."""
        # Arrange
        task_list_id = uuid.uuid4()
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
            for i in range(3)
        ]

        mock_get_tasks_use_case.execute.return_value = (tasks, 3)

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/tasks/")

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

    def test_get_tasks_with_filters(self):
        """Test getting tasks with status filter."""
        # Arrange
        mock_get_tasks_use_case.execute.return_value = ([], 0)

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/tasks/?status=completed")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 0
        assert len(response_data["items"]) == 0


class TestUpdateTaskEndpoint:
    """Test cases for PUT /api/v1/tasks/{task_id} endpoint using mocks."""

    def test_update_task_success(self):
        """Test successful task update."""
        # Arrange
        task_id = uuid.uuid4()
        task_list_id = uuid.uuid4()
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
        }

        # Original task data for reference (not used directly in mock setup)
        # existing_task = Task(
        #     id=task_id,
        #     title="Original Task Title",
        #     description="Original description",
        #     priority=TaskPriority.MEDIUM,
        #     status=TaskStatus.PENDING,
        #     task_list_id=task_list_id,
        #     created_at=datetime.now(),
        #     updated_at=datetime.now(),
        # )

        updated_task = Task(
            id=task_id,
            title=update_data["title"],
            description=update_data["description"],
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Mock get_task_use_case to return the existing task object
        # Note: The endpoint modifies the existing_task in place, so we need a fresh copy
        mock_get_task_use_case.execute.return_value = Task(
            id=task_id,
            title="Original Task Title",
            description="Original description",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_update_task_use_case.execute.return_value = updated_task

        # Act
        with TestClient(app) as client:
            response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == update_data["title"]
        assert response_data["description"] == update_data["description"]

    def test_update_task_not_found(self):
        """Test updating non-existent task returns 404."""
        # Arrange
        task_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        mock_get_task_use_case.execute.side_effect = TaskNotFoundError(task_id)

        # Act
        with TestClient(app) as client:
            response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTaskPriorityEndpoint:
    """Test cases for PATCH /api/v1/tasks/{task_id}/priority endpoint using mocks."""

    def test_update_task_priority_success(self):
        """Test successful task priority update."""
        # Arrange
        task_id = uuid.uuid4()
        task_list_id = uuid.uuid4()
        priority_data = {"priority": "high"}

        updated_task = Task(
            id=task_id,
            title="Test Task",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_update_task_priority_use_case.execute.return_value = updated_task

        # Act
        with TestClient(app) as client:
            response = client.patch(
                f"/api/v1/tasks/{task_id}/priority", json=priority_data
            )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["priority"] == "high"

    def test_update_task_priority_invalid_value(self):
        """Test updating task priority with invalid value returns 422."""
        # Arrange
        task_id = uuid.uuid4()
        priority_data = {"priority": "invalid_priority"}

        # Act
        with TestClient(app) as client:
            response = client.patch(
                f"/api/v1/tasks/{task_id}/priority", json=priority_data
            )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateTaskStatusEndpoint:
    """Test cases for PATCH /api/v1/tasks/{task_id}/status endpoint using mocks."""

    def test_update_task_status_success(self):
        """Test successful task status update."""
        # Arrange
        task_id = uuid.uuid4()
        task_list_id = uuid.uuid4()
        status_data = {"status": "completed"}

        updated_task = Task(
            id=task_id,
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.COMPLETED,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=datetime.now(),
        )

        mock_update_task_status_use_case.execute.return_value = updated_task

        # Act
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/tasks/{task_id}/status", json=status_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "completed"
        assert "completed_at" in response_data

    def test_update_task_status_invalid_value(self):
        """Test updating task status with invalid value returns 422."""
        # Arrange
        task_id = uuid.uuid4()
        status_data = {"status": "invalid_status"}

        # Act
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/tasks/{task_id}/status", json=status_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteTaskEndpoint:
    """Test cases for DELETE /api/v1/tasks/{task_id} endpoint using mocks."""

    def test_delete_task_success(self):
        """Test successful task deletion."""
        # Arrange
        task_id = uuid.uuid4()
        mock_delete_task_use_case.execute.return_value = None

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_task_not_found(self):
        """Test deleting non-existent task returns 404."""
        # Arrange
        task_id = uuid.uuid4()
        mock_delete_task_use_case.execute.side_effect = TaskNotFoundError(task_id)

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/tasks/{task_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task" in response.json()["detail"]
        assert str(task_id) in response.json()["detail"]
