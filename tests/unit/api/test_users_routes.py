"""Tests for user API routes."""

from uuid import uuid4

from fastapi.testclient import TestClient


class TestUsersRoutes:
    """Test cases for user API endpoints."""

    def test_create_user_success(self, client: TestClient):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "is_active": True,
        }

        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] == user_data["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_duplicate_email(self, client: TestClient, test_factory):
        """Test user creation with duplicate email."""
        test_factory.create_user(email="duplicate@example.com")

        user_data = {
            "email": "duplicate@example.com",
            "username": "uniqueuser",
            "full_name": "User A",
        }

        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_user_duplicate_username(self, client: TestClient, test_factory):
        """Test user creation with duplicate username."""
        test_factory.create_user(username="duplicateuser")

        user_data = {
            "email": "unique@example.com",
            "username": "duplicateuser",
            "full_name": "User B",
        }

        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_get_user_by_id_success(self, client: TestClient, test_factory):
        """Test successful user retrieval by ID."""
        user = test_factory.create_user()
        response = client.get(f"/api/v1/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["full_name"] == user.full_name
        assert data["id"] == str(user.id)

    def test_get_user_not_found(self, client: TestClient):
        """Test user retrieval with non-existent ID."""
        non_existent_id = uuid4()
        response = client.get(f"/api/v1/users/{non_existent_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_invalid_uuid(self, client: TestClient):
        """Test user retrieval with invalid UUID format."""
        response = client.get("/api/v1/users/invalid-uuid")
        assert response.status_code == 422

    def test_update_user(self, client: TestClient, test_factory):
        """Test successful user update."""
        user = test_factory.create_user()
        update_data = {"full_name": "Updated Name", "is_active": False}

        response = client.patch(f"/api/v1/users/{user.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert not data["is_active"]
        assert data["email"] == user.email
        assert data["username"] == user.username

    def test_update_user_not_found(self, client: TestClient):
        """Test user update with non-existent ID."""
        non_existent_id = uuid4()
        update_data = {"full_name": "Updated Name"}

        response = client.patch(f"/api/v1/users/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_user(self, client: TestClient, test_factory):
        """Test successful user deletion."""
        user = test_factory.create_user()
        delete_response = client.delete(f"/api/v1/users/{user.id}")
        assert delete_response.status_code == 204

        get_response = client.get(f"/api/v1/users/{user.id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Test user deletion with non-existent ID."""
        non_existent_id = uuid4()
        response = client.delete(f"/api/v1/users/{non_existent_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_users(self, client: TestClient, test_factory):
        """Test successful user listing."""
        test_factory.create_user()
        test_factory.create_user()
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert len(data["items"]) >= 2

    def test_list_users_with_pagination(self, client: TestClient, test_factory):
        """Test user listing with pagination parameters."""
        for _ in range(5):
            test_factory.create_user()

        response = client.get("/api/v1/users/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] >= 5

    def test_list_users_empty(self, client: TestClient):
        """Test user listing when no users exist."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_create_user_missing_required_fields(self, client: TestClient):
        """Test user creation without required fields."""
        user_data = {"username": "testuser", "full_name": "Test User"}
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

        user_data = {"email": "test@example.com", "full_name": "Test User"}
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    def test_create_user_invalid_email(self, client: TestClient):
        """Test user creation with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User",
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    def test_update_user_partial(self, client: TestClient, test_factory):
        """Test partial user update (only some fields)."""
        user = test_factory.create_user()
        update_data = {"full_name": "Only Name Updated"}

        response = client.patch(f"/api/v1/users/{user.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Only Name Updated"
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["is_active"] == user.is_active
