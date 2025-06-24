"""Mocked API tests for users endpoints.

These tests mock all dependencies to avoid database connections,
focusing purely on HTTP behavior and response validation.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_get_user_use_case,
    get_get_users_use_case,
    get_update_user_use_case,
)
from app.domain.exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.models.user import User
from app.main import app

# Create global mock instances
mock_create_user_use_case = AsyncMock()
mock_get_user_use_case = AsyncMock()
mock_get_users_use_case = AsyncMock()
mock_update_user_use_case = AsyncMock()
mock_delete_user_use_case = AsyncMock()


# Mock dependency functions
def get_mock_create_user_use_case():
    """Return mock create user use case."""
    return mock_create_user_use_case


def get_mock_get_user_use_case():
    """Return mock get user use case."""
    return mock_get_user_use_case


def get_mock_get_users_use_case():
    """Return mock get users use case."""
    return mock_get_users_use_case


def get_mock_update_user_use_case():
    """Return mock update user use case."""
    return mock_update_user_use_case


def get_mock_delete_user_use_case():
    """Return mock delete user use case."""
    return mock_delete_user_use_case


# Override dependencies
app.dependency_overrides[get_create_user_use_case] = get_mock_create_user_use_case
app.dependency_overrides[get_get_user_use_case] = get_mock_get_user_use_case
app.dependency_overrides[get_get_users_use_case] = get_mock_get_users_use_case
app.dependency_overrides[get_update_user_use_case] = get_mock_update_user_use_case
app.dependency_overrides[get_delete_user_use_case] = get_mock_delete_user_use_case


class TestCreateUserEndpoint:
    """Test cases for POST /api/v1/users endpoint using mocks."""

    def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
        }

        created_user = User(
            id=uuid.uuid4(),
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Mock the use case through dependency override
        mock_create_user_use_case.execute.return_value = created_user

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["last_login"] is None

    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email returns 409."""
        # Arrange
        user_data = {
            "email": "existing@example.com",
            "username": "newuser",
            "full_name": "New User",
        }

        # Mock the use case through dependency override
        mock_create_user_use_case.execute.side_effect = UserAlreadyExistsError(
            "email", "newuser@example.com"
        )

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "email" in data["detail"].lower()
        assert "already exists" in data["detail"].lower()

    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username returns 409."""
        # Arrange
        user_data = {
            "email": "new@example.com",
            "username": "existinguser",
            "full_name": "New User",
        }

        # Mock the use case through dependency override
        mock_create_user_use_case.execute.side_effect = UserAlreadyExistsError(
            "username", "newuser"
        )

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "username" in data["detail"].lower()
        assert "already exists" in data["detail"].lower()

    def test_create_user_invalid_email(self):
        """Test creating user with invalid email returns 422."""
        # Arrange
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User",
        }

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert any("email" in str(error).lower() for error in data["detail"])

    def test_create_user_missing_fields(self):
        """Test creating user with missing required fields returns 422."""
        # Arrange
        user_data = {
            "email": "test@example.com"
            # Missing username and full_name
        }

        # Act
        with TestClient(app) as client:
            response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserEndpoint:
    """Test cases for GET /api/v1/users/{user_id} endpoint using mocks."""

    def test_get_user_success(self):
        """Test successful user retrieval."""
        # Arrange
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Mock the use case through dependency override
        mock_get_user_use_case.execute.return_value = user

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(user_id)
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["full_name"] == user.full_name
        assert data["is_active"] == user.is_active

    def test_get_user_not_found(self):
        """Test getting non-existent user returns 404."""
        # Arrange
        user_id = uuid.uuid4()
        # Mock the use case through dependency override
        mock_get_user_use_case.execute.side_effect = UserNotFoundError(user_id)

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_user_invalid_uuid(self):
        """Test getting user with invalid UUID returns 422."""
        # Arrange
        invalid_uuid = "invalid-uuid"

        # Act
        with TestClient(app) as client:
            response = client.get(f"/api/v1/users/{invalid_uuid}")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


class TestGetUsersEndpoint:
    """Test cases for GET /api/v1/users endpoint using mocks."""

    def test_get_users_default_pagination(self):
        """Test getting users with default pagination."""
        # Arrange
        users = [
            User(
                id=uuid.uuid4(),
                email=f"user{i}@example.com",
                username=f"user{i}",
                full_name=f"User {i}",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(3)
        ]
        total = 3

        # Mock the use case through dependency override
        mock_get_users_use_case.execute.return_value = (users, total)

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/users")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "size" in data
        assert "total" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["size"] == 20
        assert data["total"] == total
        assert len(data["items"]) == len(users)

    def test_get_users_custom_pagination(self):
        """Test getting users with custom pagination."""
        # Arrange
        users = [
            User(
                id=uuid.uuid4(),
                email=f"user{i}@example.com",
                username=f"user{i}",
                full_name=f"User {i}",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(2)
        ]
        total = 10

        # Mock the use case through dependency override
        mock_get_users_use_case.execute.return_value = (users, total)

        # Act
        with TestClient(app) as client:
            response = client.get("/api/v1/users?page=1&size=2")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] == total
        assert len(data["items"]) == 2


class TestUpdateUserEndpoint:
    """Test cases for PUT /api/v1/users/{user_id} endpoint using mocks."""

    def test_update_user_success(self):
        """Test successful user update."""
        # Arrange
        user_id = uuid.uuid4()
        update_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User",
        }

        updated_user = User(
            id=user_id,
            email=update_data["email"],
            username=update_data["username"],
            full_name=update_data["full_name"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Mock the use case through dependency override
        mock_update_user_use_case.execute.return_value = updated_user

        # Act
        with TestClient(app) as client:
            response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(user_id)
        assert data["email"] == update_data["email"]
        assert data["username"] == update_data["username"]
        assert data["full_name"] == update_data["full_name"]

    def test_update_user_not_found(self):
        """Test updating non-existent user returns 404."""
        # Arrange
        user_id = uuid.uuid4()
        update_data = {"email": "updated@example.com"}

        # Mock the use case through dependency override
        mock_update_user_use_case.execute.side_effect = UserNotFoundError(user_id)

        # Act
        with TestClient(app) as client:
            response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestDeleteUserEndpoint:
    """Test cases for DELETE /api/v1/users/{user_id} endpoint using mocks."""

    def test_delete_user_success(self):
        """Test successful user deletion."""
        # Arrange
        user_id = uuid.uuid4()
        # Mock the use case through dependency override
        mock_delete_user_use_case.execute.return_value = None

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_user_not_found(self):
        """Test deleting non-existent user returns 404."""
        # Arrange
        user_id = uuid.uuid4()
        # Mock the use case through dependency override
        mock_delete_user_use_case.execute.side_effect = UserNotFoundError(user_id)

        # Act
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
