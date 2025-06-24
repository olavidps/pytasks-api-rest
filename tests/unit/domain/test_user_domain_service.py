"""Tests for UserDomainService."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.domain.exceptions.user import UserNotFoundError
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService


class TestUserDomainService:
    """Test cases for UserDomainService."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def user_domain_service(self, mock_user_repository):
        """Create a UserDomainService instance with mocked dependencies."""
        return UserDomainService(mock_user_repository)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
        )


class TestValidateUsernameAvailability(TestUserDomainService):
    """Test username availability validation."""

    @pytest.mark.asyncio
    async def test_username_too_short(self, user_domain_service, mock_user_repository):
        """Test that usernames shorter than 3 characters are invalid."""
        result = await user_domain_service.validate_username_availability("ab")
        assert result is False
        mock_user_repository.get_by_username.assert_not_called()

    @pytest.mark.asyncio
    async def test_username_starts_with_underscore(
        self, user_domain_service, mock_user_repository
    ):
        """Test that usernames starting with underscore are invalid."""
        result = await user_domain_service.validate_username_availability("_testuser")
        assert result is False
        mock_user_repository.get_by_username.assert_not_called()

    @pytest.mark.asyncio
    async def test_username_non_alphanumeric(
        self, user_domain_service, mock_user_repository
    ):
        """Test that usernames with special characters are invalid."""
        result = await user_domain_service.validate_username_availability("test-user")
        assert result is False
        mock_user_repository.get_by_username.assert_not_called()

    @pytest.mark.asyncio
    async def test_username_available(self, user_domain_service, mock_user_repository):
        """Test that available usernames return True."""
        mock_user_repository.get_by_username = AsyncMock(
            side_effect=UserNotFoundError("User not found")
        )

        result = await user_domain_service.validate_username_availability("testuser")

        assert result is True
        mock_user_repository.get_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_username_taken(
        self, user_domain_service, mock_user_repository, sample_user
    ):
        """Test that taken usernames return False."""
        mock_user_repository.get_by_username = AsyncMock(return_value=sample_user)

        result = await user_domain_service.validate_username_availability("testuser")

        assert result is False
        mock_user_repository.get_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_username_taken_but_excluded(
        self, user_domain_service, mock_user_repository, sample_user
    ):
        """Test that taken usernames return True when user is excluded."""
        mock_user_repository.get_by_username = AsyncMock(return_value=sample_user)

        result = await user_domain_service.validate_username_availability(
            "testuser", exclude_user_id=str(sample_user.id)
        )

        assert result is True
        mock_user_repository.get_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_username_with_underscores(
        self, user_domain_service, mock_user_repository
    ):
        """Test that usernames with underscores (not at start) are valid."""
        mock_user_repository.get_by_username = AsyncMock(
            side_effect=UserNotFoundError("User not found")
        )

        result = await user_domain_service.validate_username_availability("test_user")

        assert result is True
        mock_user_repository.get_by_username.assert_called_once_with("test_user")


class TestValidateEmailAvailability(TestUserDomainService):
    """Test email availability validation."""

    @pytest.mark.asyncio
    async def test_email_available(self, user_domain_service, mock_user_repository):
        """Test that available emails return True."""
        mock_user_repository.get_by_email = AsyncMock(
            side_effect=UserNotFoundError("User not found")
        )

        result = await user_domain_service.validate_email_availability(
            "test@example.com"
        )

        assert result is True
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_email_taken(
        self, user_domain_service, mock_user_repository, sample_user
    ):
        """Test that taken emails return False."""
        mock_user_repository.get_by_email = AsyncMock(return_value=sample_user)

        result = await user_domain_service.validate_email_availability(
            "test@example.com"
        )

        assert result is False
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_email_taken_but_excluded(
        self, user_domain_service, mock_user_repository, sample_user
    ):
        """Test that taken emails return True when user is excluded."""
        mock_user_repository.get_by_email = AsyncMock(return_value=sample_user)

        result = await user_domain_service.validate_email_availability(
            "test@example.com", exclude_user_id=str(sample_user.id)
        )

        assert result is True
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")


class TestCanUserBeDeleted(TestUserDomainService):
    """Test user deletion validation."""

    @pytest.mark.asyncio
    async def test_user_not_found(self, user_domain_service, mock_user_repository):
        """Test deletion check when user doesn't exist."""
        mock_user_repository.get_by_id = AsyncMock(return_value=None)

        can_delete, reason = await user_domain_service.can_user_be_deleted(
            "nonexistent-id"
        )

        assert can_delete is False
        assert reason == "User not found"
        mock_user_repository.get_by_id.assert_called_once_with("nonexistent-id")

    @pytest.mark.asyncio
    async def test_user_can_be_deleted(
        self, user_domain_service, mock_user_repository, sample_user
    ):
        """Test deletion check when user can be safely deleted."""
        mock_user_repository.get_by_id = AsyncMock(return_value=sample_user)

        can_delete, reason = await user_domain_service.can_user_be_deleted(
            str(sample_user.id)
        )

        assert can_delete is True
        assert reason == "User can be safely deleted"
        mock_user_repository.get_by_id.assert_called_once_with(str(sample_user.id))
