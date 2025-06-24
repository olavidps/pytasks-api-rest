"""Unit tests for user domain service."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.models.user import User
from app.domain.services.user_domain_service import UserDomainService


class TestUserDomainService:
    """Test cases for UserDomainService."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def user_domain_service(self, mock_user_repository):
        """User domain service instance."""
        return UserDomainService(mock_user_repository)

    async def test_validate_email_availability_success(
        self, user_domain_service, mock_user_repository
    ):
        """Test email validation when email is available."""
        # Arrange
        email = "available@example.com"
        mock_user_repository.get_by_email.return_value = None

        # Act
        result = await user_domain_service.validate_email_availability(email)

        # Assert
        assert result is True
        mock_user_repository.get_by_email.assert_called_once_with(email)

    async def test_validate_email_availability_with_exclude_id(
        self, user_domain_service, mock_user_repository
    ):
        """Test email validation when email exists but belongs to excluded user."""
        # Arrange
        email = "test@example.com"
        user_id = uuid4()
        existing_user = User(
            id=user_id,
            email=email,
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        mock_user_repository.get_by_email.return_value = existing_user

        # Act
        result = await user_domain_service.validate_email_availability(
            email, exclude_user_id=str(user_id)
        )

        # Assert
        assert result is True
        mock_user_repository.get_by_email.assert_called_once_with(email)

    async def test_validate_email_availability_already_exists(
        self, user_domain_service, mock_user_repository
    ):
        """Test email validation when email already exists."""
        # Arrange
        email = "existing@example.com"
        existing_user = User(
            id=uuid4(),
            email=email,
            username="existinguser",
            full_name="Existing User",
            is_active=True,
        )

        mock_user_repository.get_by_email.return_value = existing_user

        # Act
        result = await user_domain_service.validate_email_availability(email)

        # Assert
        assert result is False
        mock_user_repository.get_by_email.assert_called_once_with(email)

    async def test_validate_email_availability_exists_different_user(
        self, user_domain_service, mock_user_repository
    ):
        """Test email validation when email exists for different user."""
        # Arrange
        email = "test@example.com"
        existing_user_id = uuid4()
        different_user_id = uuid4()

        existing_user = User(
            id=existing_user_id,
            email=email,
            username="existinguser",
            full_name="Existing User",
            is_active=True,
        )

        mock_user_repository.get_by_email.return_value = existing_user

        # Act
        result = await user_domain_service.validate_email_availability(
            email, exclude_user_id=str(different_user_id)
        )

        # Assert
        assert result is False
        mock_user_repository.get_by_email.assert_called_once_with(email)

    async def test_validate_username_availability_success(
        self, user_domain_service, mock_user_repository
    ):
        """Test username validation when username is available."""
        # Arrange
        username = "availableuser"
        mock_user_repository.get_by_username.return_value = None

        # Act
        result = await user_domain_service.validate_username_availability(username)

        # Assert
        assert result is True
        mock_user_repository.get_by_username.assert_called_once_with(username)

    async def test_validate_username_availability_with_exclude_id(
        self, user_domain_service, mock_user_repository
    ):
        """Test username validation when username exists but belongs to excluded user."""
        # Arrange
        username = "testuser"
        user_id = uuid4()
        existing_user = User(
            id=user_id,
            email="test@example.com",
            username=username,
            full_name="Test User",
            is_active=True,
        )

        mock_user_repository.get_by_username.return_value = existing_user

        # Act
        result = await user_domain_service.validate_username_availability(
            username, exclude_user_id=str(user_id)
        )

        # Assert
        assert result is True
        mock_user_repository.get_by_username.assert_called_once_with(username)

    async def test_validate_username_availability_already_exists(
        self, user_domain_service, mock_user_repository
    ):
        """Test username validation when username already exists."""
        # Arrange
        username = "existinguser"
        existing_user = User(
            id=uuid4(),
            email="existing@example.com",
            username=username,
            full_name="Existing User",
            is_active=True,
        )

        mock_user_repository.get_by_username.return_value = existing_user

        # Act
        result = await user_domain_service.validate_username_availability(username)

        # Assert
        assert result is False
        mock_user_repository.get_by_username.assert_called_once_with(username)

    async def test_validate_username_availability_exists_different_user(
        self, user_domain_service, mock_user_repository
    ):
        """Test username validation when username exists for different user."""
        # Arrange
        username = "testuser"
        existing_user_id = uuid4()
        different_user_id = uuid4()

        existing_user = User(
            id=existing_user_id,
            email="existing@example.com",
            username=username,
            full_name="Existing User",
            is_active=True,
        )

        mock_user_repository.get_by_username.return_value = existing_user

        # Act
        result = await user_domain_service.validate_username_availability(
            username, exclude_user_id=str(different_user_id)
        )

        # Assert
        assert result is False
        mock_user_repository.get_by_username.assert_called_once_with(username)
