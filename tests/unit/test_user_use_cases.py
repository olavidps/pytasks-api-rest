"""Unit tests for user use cases."""

from unittest import mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.api.schemas.common_schemas import (
    FilterParams,
    PaginatedResponse,
    PaginationParams,
)
from app.api.schemas.user_schemas import UserUpdate
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.get_users import GetUsersUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.domain.models.user import User


class TestCreateUserUseCase:
    """Test cases for CreateUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_validation_service(self):
        """Mock user validation service."""
        return AsyncMock()

    @pytest.fixture
    def create_user_use_case(self, mock_user_repository, mock_user_validation_service):
        """Create user use case instance."""
        return CreateUserUseCase(mock_user_repository, mock_user_validation_service)

    async def test_create_user_success(
        self, create_user_use_case, mock_user_repository, mock_user_validation_service
    ):
        """Test successful user creation."""
        # Arrange
        user_data = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        created_user = User(
            id=uuid4(),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=True,
        )

        mock_user_validation_service.validate_user_availability.return_value = None
        mock_user_repository.create.return_value = created_user

        # Act
        result = await create_user_use_case.execute(user_data)

        # Assert
        assert result == created_user
        mock_user_validation_service.validate_user_availability.assert_called_once_with(
            user_data
        )
        mock_user_repository.create.assert_called_once_with(user_data)

    async def test_create_user_email_already_exists(
        self, create_user_use_case, mock_user_validation_service
    ):
        """Test creating user with existing email raises exception."""
        # Arrange
        user_data = User(
            email="existing@example.com", username="testuser", full_name="Test User"
        )

        mock_user_validation_service.validate_user_availability.side_effect = (
            UserAlreadyExistsError("email", "existing@example.com")
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await create_user_use_case.execute(user_data)

        mock_user_validation_service.validate_user_availability.assert_called_once_with(
            user_data
        )

    async def test_create_user_username_already_exists(
        self, create_user_use_case, mock_user_validation_service
    ):
        """Test creating user with existing username raises exception."""
        # Arrange
        user_data = User(
            email="test@example.com", username="existinguser", full_name="Test User"
        )

        mock_user_validation_service.validate_user_availability.side_effect = (
            UserAlreadyExistsError("username", "existinguser")
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await create_user_use_case.execute(user_data)

        mock_user_validation_service.validate_user_availability.assert_called_once_with(
            user_data
        )


class TestGetUserUseCase:
    """Test cases for GetUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def get_user_use_case(self, mock_user_repository):
        """Get user use case instance."""
        return GetUserUseCase(mock_user_repository)

    async def test_get_user_success(self, get_user_use_case, mock_user_repository):
        """Test successful user retrieval."""
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        mock_user_repository.get_by_id.return_value = user

        # Act
        result = await get_user_use_case.execute(user_id)

        # Assert
        assert result == user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    async def test_get_user_not_found(self, get_user_use_case, mock_user_repository):
        """Test getting non-existent user raises exception."""
        # Arrange
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await get_user_use_case.execute(user_id)

        mock_user_repository.get_by_id.assert_called_once_with(user_id)


class TestGetUsersUseCase:
    """Test cases for GetUsersUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def get_users_use_case(self, mock_user_repository):
        """Get users use case instance."""
        return GetUsersUseCase(mock_user_repository)

    async def test_get_users_success(self, get_users_use_case, mock_user_repository):
        """Test successful users retrieval with pagination."""
        # Arrange
        filters = FilterParams()
        pagination = PaginationParams(page=1, size=20)

        users = [
            User(
                id=uuid4(),
                email="user1@example.com",
                username="user1",
                full_name="User One",
                is_active=True,
            ),
            User(
                id=uuid4(),
                email="user2@example.com",
                username="user2",
                full_name="User Two",
                is_active=True,
            ),
        ]

        total_count = 2
        _ = PaginatedResponse(items=users, page=1, size=20, total=total_count, pages=1)

        mock_user_repository.get_paginated.return_value = (users, total_count)

        # Act
        users_result, total_result = await get_users_use_case.execute(
            pagination, filters
        )

        # Assert
        assert users_result == users
        assert total_result == total_count
        mock_user_repository.get_paginated.assert_called_once_with(
            offset=pagination.offset, limit=pagination.size, filters={}
        )

    async def test_get_users_with_filters(
        self, get_users_use_case, mock_user_repository
    ):
        """Test users retrieval with filters."""
        # Arrange
        filters = FilterParams(search="test", is_active=True)
        pagination = PaginationParams(page=1, size=10)

        users = []
        total_count = 0

        mock_user_repository.get_paginated.return_value = (users, total_count)

        # Act
        users_result, total_result = await get_users_use_case.execute(
            pagination, filters
        )

        # Assert
        assert users_result == []
        assert total_result == 0
        mock_user_repository.get_paginated.assert_called_once_with(
            offset=pagination.offset,
            limit=pagination.size,
            filters={"search": "test", "is_active": True},
        )


class TestUpdateUserUseCase:
    """Test cases for UpdateUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_domain_service(self):
        """Mock user domain service."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_validation_service(self):
        """Mock user validation service."""
        return AsyncMock()

    @pytest.fixture
    def update_user_use_case(self, mock_user_repository, mock_user_validation_service):
        """Update user use case instance."""
        return UpdateUserUseCase(mock_user_repository, mock_user_validation_service)

    async def test_update_user_success(
        self, update_user_use_case, mock_user_repository, mock_user_validation_service
    ):
        """Test successful user update."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(
            email="updated@example.com",
            username="updateduser",
            full_name="Updated User",
        )

        existing_user = User(
            id=user_id,
            email="old@example.com",
            username="olduser",
            full_name="Old User",
            is_active=True,
        )

        updated_user = User(
            id=user_id,
            email=update_data.email,
            username=update_data.username,
            full_name=update_data.full_name,
            is_active=True,
        )

        mock_user_repository.get_by_id.return_value = existing_user
        mock_user_validation_service.validate_user_availability.return_value = None
        mock_user_repository.update.return_value = updated_user

        # Act
        result = await update_user_use_case.execute(user_id, update_data)

        # Assert
        assert result == updated_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_validation_service.validate_user_availability.assert_called_once()
        mock_user_repository.update.assert_called_once_with(user_id, mock.ANY)

    async def test_update_user_not_found(
        self, update_user_use_case, mock_user_repository
    ):
        """Test updating non-existent user raises exception."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(email="updated@example.com")

        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await update_user_use_case.execute(user_id, update_data)

        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    async def test_update_user_partial_update(
        self, update_user_use_case, mock_user_repository, mock_user_validation_service
    ):
        """Test partial user update (only email)."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(email="updated@example.com")

        existing_user = User(
            id=user_id,
            email="old@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        updated_user = User(
            id=user_id,
            email=update_data.email,
            username=existing_user.username,
            full_name=existing_user.full_name,
            is_active=True,
        )

        mock_user_repository.get_by_id.return_value = existing_user
        mock_user_validation_service.validate_user_availability.return_value = None
        mock_user_repository.update.return_value = updated_user

        # Act
        result = await update_user_use_case.execute(user_id, update_data)

        # Assert
        assert result == updated_user
        mock_user_validation_service.validate_user_availability.assert_called_once()


class TestDeleteUserUseCase:
    """Test cases for DeleteUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def delete_user_use_case(self, mock_user_repository):
        """Delete user use case instance."""
        return DeleteUserUseCase(mock_user_repository)

    async def test_delete_user_success(
        self, delete_user_use_case, mock_user_repository
    ):
        """Test successful user deletion."""
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        mock_user_repository.get_by_id.return_value = user
        mock_user_repository.delete.return_value = None

        # Act
        await delete_user_use_case.execute(user_id)

        # Assert
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.delete.assert_called_once_with(user_id)

    async def test_delete_user_not_found(
        self, delete_user_use_case, mock_user_repository
    ):
        """Test deleting non-existent user raises exception."""
        # Arrange
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await delete_user_use_case.execute(user_id)

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.delete.assert_not_called()
