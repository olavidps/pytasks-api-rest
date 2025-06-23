"""Tests for task list API routes."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


class TestTaskListsRoutes:
    """Test cases for task list API endpoints."""

    @pytest.mark.asyncio
    async def test_create_task_list_success(self, client: TestClient, test_factory):
        """Test successful task list creation."""
        owner = await test_factory.create_user()

        task_list_data = {
            "name": "My Task List",
            "description": "A list for my tasks",
            "owner_id": str(owner.id),
        }

        response = client.post("/api/v1/task-lists", json=task_list_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == task_list_data["name"]
        assert data["description"] == task_list_data["description"]
        assert data["owner_id"] == task_list_data["owner_id"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_task_list_without_description(
        self, client: TestClient, test_factory
    ):
        """Test task list creation without description."""
        owner = await test_factory.create_user()

        task_list_data = {"name": "My Task List", "owner_id": str(owner.id)}

        response = client.post("/api/v1/task-lists", json=task_list_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == task_list_data["name"]
        assert data["description"] is None
        assert data["owner_id"] == task_list_data["owner_id"]

    @pytest.mark.asyncio
    async def test_create_task_list_invalid_owner(self, client: TestClient):
        """Test task list creation with non-existent owner."""
        non_existent_owner_id = uuid4()

        task_list_data = {
            "name": "My Task List",
            "owner_id": str(non_existent_owner_id),
        }

        response = client.post("/api/v1/task-lists", json=task_list_data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_task_list_missing_name(
        self, client: TestClient, test_factory
    ):
        """Test task list creation without required name field."""
        owner = await test_factory.create_user()

        task_list_data = {"owner_id": str(owner.id)}

        response = client.post("/api/v1/task-lists", json=task_list_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_task_list_by_id_success(self, client: TestClient, test_factory):
        """Test successful task list retrieval by ID."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        response = client.get(f"/api/v1/task-lists/{task_list.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(task_list.id)
        assert data["name"] == task_list.name
        assert data["description"] == task_list.description
        assert data["owner_id"] == str(task_list.owner_id)

    def test_get_task_list_by_id_not_found(self, client: TestClient):
        """Test task list retrieval with non-existent ID."""
        non_existent_id = uuid4()

        response = client.get(f"/api/v1/task-lists/{non_existent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_task_list_by_id_invalid_uuid(self, client: TestClient):
        """Test task list retrieval with invalid UUID format."""
        response = client.get("/api/v1/task-lists/invalid-uuid")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_task_list_success(self, client: TestClient, test_factory):
        """Test successful task list update."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        update_data = {
            "name": "Updated Task List",
            "description": "Updated description",
            "is_active": False,
        }

        response = client.patch(f"/api/v1/task-lists/{task_list.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_active"] == update_data["is_active"]
        assert data["owner_id"] == str(task_list.owner_id)  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_task_list_partial(self, client: TestClient, test_factory):
        """Test partial task list update."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        update_data = {"name": "Partially Updated"}

        response = client.patch(f"/api/v1/task-lists/{task_list.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == task_list.description  # Should remain unchanged
        assert data["is_active"] == task_list.is_active  # Should remain unchanged

    def test_update_task_list_not_found(self, client: TestClient):
        """Test task list update with non-existent ID."""
        non_existent_id = uuid4()
        update_data = {"name": "Updated Name"}

        response = client.patch(
            f"/api/v1/task-lists/{non_existent_id}", json=update_data
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_task_list_success(self, client: TestClient, test_factory):
        """Test successful task list deletion."""
        owner = await test_factory.create_user()
        task_list = await test_factory.create_task_list(owner)

        response = client.delete(f"/api/v1/task-lists/{task_list.id}")

        assert response.status_code == 204

        # Verify task list is deleted
        get_response = client.get(f"/api/v1/task-lists/{task_list.id}")
        assert get_response.status_code == 404

    def test_delete_task_list_not_found(self, client: TestClient):
        """Test task list deletion with non-existent ID."""
        non_existent_id = uuid4()

        response = client.delete(f"/api/v1/task-lists/{non_existent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_list_task_lists_success(self, client: TestClient, test_factory):
        """Test successful task list listing."""
        owner = await test_factory.create_user()
        [await test_factory.create_task_list(owner) for _ in range(3)]

        response = client.get("/api/v1/task-lists")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_list_task_lists_with_pagination(
        self, client: TestClient, test_factory
    ):
        """Test task list listing with pagination parameters."""
        owner = await test_factory.create_user()
        [await test_factory.create_task_list(owner) for _ in range(5)]

        response = client.get("/api/v1/task-lists?page=1&size=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] >= 5

    @pytest.mark.asyncio
    async def test_list_task_lists_filter_by_owner(
        self, client: TestClient, test_factory
    ):
        """Test task list listing filtered by owner."""
        owner1 = await test_factory.create_user()
        owner2 = await test_factory.create_user()

        [await test_factory.create_task_list(owner1) for _ in range(2)]
        [await test_factory.create_task_list(owner2) for _ in range(3)]

        response = client.get(f"/api/v1/task-lists?owner_id={owner1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["owner_id"] == str(owner1.id)

    @pytest.mark.asyncio
    async def test_list_task_lists_filter_by_active_status(
        self, client: TestClient, test_factory
    ):
        """Test task list listing filtered by active status."""
        owner = await test_factory.create_user()

        # Create active task lists
        active_task_lists = [
            await test_factory.create_task_list(owner, is_active=True) for _ in range(2)
        ]

        # Create inactive task lists
        inactive_task_lists = [
            await test_factory.create_task_list(owner, is_active=False)
            for _ in range(1)
        ]

        response = client.get("/api/v1/task-lists?is_active=true")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 2
        for item in data["items"]:
            assert item["is_active"] is True

    def test_list_task_lists_empty(self, client: TestClient):
        """Test task list listing when no task lists exist."""
        response = client.get("/api/v1/task-lists")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_list_task_lists_invalid_owner_id(self, client: TestClient):
        """Test task list listing with invalid owner ID format."""
        response = client.get("/api/v1/task-lists?owner_id=invalid-uuid")

        assert response.status_code == 422
