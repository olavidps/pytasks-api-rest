"""Tests for task API routes."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.models.task import TaskPriority, TaskStatus


class TestTasksRoutes:
    """Test cases for task API endpoints."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client: TestClient, test_factory):
        """Test successful task creation."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        assignee = await test_factory.create_user()

        due_date = (datetime.now() + timedelta(days=7)).isoformat()

        task_data = {
            "title": "New Task",
            "description": "Task description",
            "status": "pending",
            "priority": "high",
            "task_list_id": str(task_list.id),
            "assigned_to_id": str(assignee.id),
            "due_date": due_date,
        }

        response = client.post("/api/v1/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]
        assert data["task_list_id"] == task_data["task_list_id"]
        assert data["assigned_to_id"] == task_data["assigned_to_id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_task_minimal_data(self, client: TestClient, test_factory):
        """Test task creation with minimal required data."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        task_data = {"title": "Minimal Task", "task_list_id": str(task_list.id)}

        response = client.post("/api/v1/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["task_list_id"] == task_data["task_list_id"]
        assert data["description"] is None
        assert data["status"] == "pending"  # Default status
        assert data["priority"] == "medium"  # Default priority
        assert data["assigned_to_id"] is None
        assert data["due_date"] is None

    def test_create_task_invalid_task_list(self, client: TestClient):
        """Test task creation with non-existent task list."""
        non_existent_task_list_id = uuid4()

        task_data = {
            "title": "New Task",
            "task_list_id": str(non_existent_task_list_id),
        }

        response = client.post("/api/v1/tasks", json=task_data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_task_invalid_assignee(self, client: TestClient, test_factory):
        """Test task creation with non-existent assignee."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        non_existent_user_id = uuid4()

        task_data = {
            "title": "New Task",
            "task_list_id": str(task_list.id),
            "assigned_to_id": str(non_existent_user_id),
        }

        response = client.post("/api/v1/tasks", json=task_data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_task_missing_title(self, client: TestClient, test_factory):
        """Test task creation without required title field."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        task_data = {"task_list_id": str(task_list.id)}

        response = client.post("/api/v1/tasks", json=task_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_task_by_id_success(self, client: TestClient, test_factory):
        """Test successful task retrieval by ID."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        task = await test_factory.create_task(task_list)

        response = client.get(f"/api/v1/tasks/{task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(task.id)
        assert data["title"] == task.title
        assert data["description"] == task.description
        assert data["task_list_id"] == str(task.task_list_id)

    def test_get_task_by_id_not_found(self, client: TestClient):
        """Test task retrieval with non-existent ID."""
        non_existent_id = uuid4()

        response = client.get(f"/api/v1/tasks/{non_existent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_task_by_id_invalid_uuid(self, client: TestClient):
        """Test task retrieval with invalid UUID format."""
        response = client.get("/api/v1/tasks/invalid-uuid")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_task_success(self, client: TestClient, test_factory):
        """Test successful task update."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        task = await test_factory.create_task(task_list)
        assignee = await test_factory.create_user()

        update_data = {
            "title": "Updated Task",
            "description": "Updated description",
            "status": "completed",
            "priority": "low",
            "assigned_to_id": str(assignee.id),
        }

        response = client.patch(f"/api/v1/tasks/{task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
        assert data["assigned_to_id"] == update_data["assigned_to_id"]
        assert data["task_list_id"] == str(task.task_list_id)  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_task_partial(self, client: TestClient, test_factory):
        """Test partial task update."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        task = await test_factory.create_task(task_list)

        update_data = {"status": "in_progress"}

        response = client.patch(f"/api/v1/tasks/{task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["title"] == task.title  # Should remain unchanged
        assert data["description"] == task.description  # Should remain unchanged

    def test_update_task_not_found(self, client: TestClient):
        """Test task update with non-existent ID."""
        non_existent_id = uuid4()
        update_data = {"title": "Updated Title"}

        response = client.patch(f"/api/v1/tasks/{non_existent_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_task_invalid_assignee(self, client: TestClient, test_factory):
        """Test task update with non-existent assignee."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        task = await test_factory.create_task(task_list)
        non_existent_user_id = uuid4()

        update_data = {"assigned_to_id": str(non_existent_user_id)}

        response = client.patch(f"/api/v1/tasks/{task.id}", json=update_data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client: TestClient, test_factory):
        """Test successful task deletion."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        task = await test_factory.create_task(task_list)

        response = client.delete(f"/api/v1/tasks/{task.id}")

        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(f"/api/v1/tasks/{task.id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        """Test task deletion with non-existent ID."""
        non_existent_id = uuid4()

        response = client.delete(f"/api/v1/tasks/{non_existent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_list_tasks_success(self, client: TestClient, test_factory):
        """Test successful task listing."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        [await test_factory.create_task(task_list) for _ in range(3)]

        response = client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_with_pagination(self, client: TestClient, test_factory):
        """Test task listing with pagination parameters."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)
        [await test_factory.create_task(task_list) for _ in range(5)]

        response = client.get("/api/v1/tasks?page=1&size=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] >= 5

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_task_list(
        self, client: TestClient, test_factory
    ):
        """Test task listing filtered by task list."""
        owner = await test_factory.create_user()
        task_list1 = await test_factory.create_task_list(owner)
        task_list2 = await test_factory.create_task_list(owner)

        [await test_factory.create_task(task_list1) for _ in range(2)]
        [await test_factory.create_task(task_list2) for _ in range(3)]

        response = client.get(f"/api/v1/tasks?task_list_id={task_list1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["task_list_id"] == str(task_list1.id)

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, client: TestClient, test_factory):
        """Test task listing filtered by status."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        pending_tasks = [
            await test_factory.create_task(task_list, status=TaskStatus.PENDING)
            for _ in range(2)
        ]
        completed_tasks = [
            await test_factory.create_task(task_list, status=TaskStatus.COMPLETED)
            for _ in range(1)
        ]

        response = client.get("/api/v1/tasks?status=pending")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 2
        for item in data["items"]:
            assert item["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(
        self, client: TestClient, test_factory
    ):
        """Test task listing filtered by priority."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        high_priority_tasks = [
            await test_factory.create_task(task_list, priority=TaskPriority.HIGH)
            for _ in range(2)
        ]
        low_priority_tasks = [
            await test_factory.create_task(task_list, priority=TaskPriority.LOW)
            for _ in range(1)
        ]

        response = client.get("/api/v1/tasks?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 2
        for item in data["items"]:
            assert item["priority"] == "high"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_assigned_user(
        self, client: TestClient, test_factory
    ):
        """Test task listing filtered by assigned user."""
        owner = await test_factory.create_user()
        assignee1 = await test_factory.create_user()
        assignee2 = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        # Create tasks with different assignees
        task1 = await test_factory.create_task(task_list, assigned_user=assignee1)
        task2 = await test_factory.create_task(task_list, assigned_user=assignee2)
        await test_factory.create_task(task_list)

        response = client.get(f"/api/v1/tasks?assigned_to_id={assignee1.id}")

        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            if item["assigned_to_id"] is not None:
                assert item["assigned_to_id"] == str(assignee1.id)

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_date_range(
        self, client: TestClient, test_factory
    ):
        """Test task listing filtered by due date range."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        # Create tasks with different due dates
        task1 = await test_factory.create_task(
            task_list, due_date=datetime.now() + timedelta(days=1)
        )
        task2 = await test_factory.create_task(
            task_list, due_date=datetime.now() + timedelta(days=10)
        )
        task3 = await test_factory.create_task(
            task_list, due_date=datetime.now() + timedelta(days=20)
        )

        # Filter tasks due within next 7 days
        due_date_from = datetime.now().isoformat()
        due_date_to = (datetime.now() + timedelta(days=7)).isoformat()

        response = client.get(
            f"/api/v1/tasks?due_date_from={due_date_from}&due_date_to={due_date_to}"
        )

        assert response.status_code == 200
        data = response.json()
        # Should include task1 but not task2 or task3
        for item in data["items"]:
            if item["due_date"] is not None:
                due_date = datetime.fromisoformat(
                    item["due_date"].replace("Z", "+00:00")
                )
                assert due_date <= datetime.now() + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_list_tasks_multiple_filters(self, client: TestClient, test_factory):
        """Test task listing with multiple filters combined."""
        owner = await test_factory.create_user()
        assignee = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        # Create a task that matches all filters
        matching_task = await test_factory.create_task(
            task_list,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            assigned_user=assignee,
        )

        # Create tasks that don't match all filters
        non_matching_task1 = await test_factory.create_task(
            task_list, status=TaskStatus.COMPLETED, priority=TaskPriority.HIGH
        )

        non_matching_task2 = await test_factory.create_task(
            task_list, status=TaskStatus.PENDING, priority=TaskPriority.LOW
        )

        response = client.get(
            f"/api/v1/tasks?task_list_id={task_list.id}&status=pending&priority=high&assigned_to_id={assignee.id}"
        )

        assert response.status_code == 200
        data = response.json()
        # Should only include the matching task
        for item in data["items"]:
            assert item["task_list_id"] == str(task_list.id)
            assert item["status"] == "pending"
            assert item["priority"] == "high"
            assert item["assigned_to_id"] == str(assignee.id)

    def test_list_tasks_empty(self, client: TestClient):
        """Test task listing when no tasks exist."""
        response = client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_list_tasks_invalid_filters(self, client: TestClient):
        """Test task listing with invalid filter values."""
        # Test invalid UUID
        response = client.get("/api/v1/tasks?task_list_id=invalid-uuid")
        assert response.status_code == 422

        # Test invalid status
        response = client.get("/api/v1/tasks?status=invalid-status")
        assert response.status_code == 422

        # Test invalid priority
        response = client.get("/api/v1/tasks?priority=invalid-priority")
        assert response.status_code == 422
