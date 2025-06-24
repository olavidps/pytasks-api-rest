"""Unit tests for user repository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestUserRepository:
    """Test cases for UserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock async database session."""
        session = MagicMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def user_repository(self, mock_session):
        """User repository instance."""
        return UserRepositoryImpl(mock_session)

    async def test_create_user_success(self, user_repository, mock_session):
        """Test successful user creation."""
        # Arrange
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        # Mock the _to_domain method to return the expected User
        user_repository._to_domain = MagicMock(return_value=user)

        # Act
        result = await user_repository.create(user)

        # Assert
        assert isinstance(result, User)
        assert result.email == user.email
        assert result.username == user.username
        assert result.full_name == user.full_name
        assert result.is_active is True

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_get_by_id_success(self, user_repository, mock_session):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        user_model = MagicMock()
        user_model.id = user_id
        user_model.email = "test@example.com"
        user_model.username = "testuser"
        user_model.full_name = "Test User"
        user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_model
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method
        user_repository._to_domain = MagicMock(return_value=user)

        # Act
        result = await user_repository.get_by_id(user_id)

        # Assert
        assert result == user
        mock_session.execute.assert_called_once()

    async def test_exists_user_true(self, user_repository, mock_session):
        """Test user exists returns True."""
        # Arrange
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_id  # User exists
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.exists(user_id)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()

    async def test_exists_user_false(self, user_repository, mock_session):
        """Test user exists returns False."""
        # Arrange
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # User doesn't exist
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.exists(user_id)

        # Assert
        assert result is False
        mock_session.execute.assert_called_once()

    async def test_email_exists_true(self, user_repository, mock_session):
        """Test email exists returns True."""
        # Arrange
        email = "test@example.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1  # Email exists
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.email_exists(email)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()

    async def test_username_exists_true(self, user_repository, mock_session):
        """Test username exists returns True."""
        # Arrange
        username = "testuser"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1  # Username exists
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.username_exists(username)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_by_id_not_found(self, user_repository, mock_session):
        """Test user retrieval by ID when user doesn't exist."""
        # Arrange
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.get_by_id(user_id)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_by_email_success(self, user_repository, mock_session):
        """Test successful user retrieval by email."""
        # Arrange
        email = "test@example.com"
        user = User(
            id=uuid4(),
            email=email,
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        user_model = MagicMock()
        user_model.id = user.id
        user_model.email = email
        user_model.username = "testuser"
        user_model.full_name = "Test User"
        user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_model
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method
        user_repository._to_domain = MagicMock(return_value=user)

        # Act
        result = await user_repository.get_by_email(email)

        # Assert
        assert result == user
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_by_email_not_found(self, user_repository, mock_session):
        """Test user retrieval by email when user doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.get_by_email(email)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_by_username_success(self, user_repository, mock_session):
        """Test successful user retrieval by username."""
        # Arrange
        username = "testuser"
        user = User(
            id=uuid4(),
            email="test@example.com",
            username=username,
            full_name="Test User",
            is_active=True,
        )

        user_model = MagicMock()
        user_model.id = user.id
        user_model.email = "test@example.com"
        user_model.username = username
        user_model.full_name = "Test User"
        user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_model
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method
        user_repository._to_domain = MagicMock(return_value=user)

        # Act
        result = await user_repository.get_by_username(username)

        # Assert
        assert result == user
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_by_username_not_found(self, user_repository, mock_session):
        """Test user retrieval by username when user doesn't exist."""
        # Arrange
        username = "nonexistentuser"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await user_repository.get_by_username(username)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    async def test_get_paginated_success(self, user_repository, mock_session):
        """Test successful paginated user retrieval."""
        # Arrange
        offset = 0
        limit = 20
        filters = None

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

        user_models = [
            MagicMock(
                id=users[0].id,
                email="user1@example.com",
                username="user1",
                full_name="User One",
                is_active=True,
            ),
            MagicMock(
                id=users[1].id,
                email="user2@example.com",
                username="user2",
                full_name="User Two",
                is_active=True,
            ),
        ]

        # Mock the results for both queries (data and count)
        # First call returns count, second call returns data
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = len(users)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = user_models

        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        # Mock the _to_domain method to convert each model to domain object
        user_repository._to_domain = MagicMock(side_effect=[users[0], users[1]])

        # Act
        result_users, total_count = await user_repository.get_paginated(
            offset, limit, filters
        )

        # Assert
        assert len(result_users) == 2
        assert total_count == 2
        assert mock_session.execute.call_count == 2
        assert result_users[0].email == "user1@example.com"
        assert result_users[1].email == "user2@example.com"

    async def test_get_paginated_with_filters(self, user_repository, mock_session):
        """Test paginated user retrieval with filters."""
        # Arrange
        offset = 0
        limit = 10
        filters = {"search": "test", "is_active": True}

        user_models = []

        # Mock the results
        # First call returns count, second call returns data
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = user_models

        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value = mock_scalars

        mock_session.execute.side_effect = [mock_count_result, mock_data_result]

        # Mock the _to_domain method (no users to convert)
        user_repository._to_domain = MagicMock()

        # Act
        result_users, total_count = await user_repository.get_paginated(
            offset, limit, filters
        )

        # Assert
        assert result_users == []
        assert total_count == 0
        assert mock_session.execute.call_count == 2

    async def test_update_user_success(self, user_repository, mock_session):
        """Test successful user update."""
        # Arrange
        user_id = str(uuid4())
        updated_user = User(
            id=user_id,
            email="updated@example.com",
            username="updateduser",
            full_name="Updated User",
            is_active=True,
        )

        existing_user_model = MagicMock()
        existing_user_model.id = user_id
        existing_user_model.email = "old@example.com"
        existing_user_model.username = "olduser"
        existing_user_model.full_name = "Old User"
        existing_user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user_model
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method
        user_repository._to_domain = MagicMock(return_value=updated_user)

        # Act
        result = await user_repository.update(user_id, updated_user)

        # Assert
        assert result == updated_user
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_user_model)

    async def test_update_user_partial(self, user_repository, mock_session):
        """Test partial user update."""
        # Arrange
        user_id = str(uuid4())
        updated_user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Updated Name",  # Only this field is updated
            is_active=True,
        )

        existing_user_model = MagicMock()
        existing_user_model.id = user_id
        existing_user_model.email = "test@example.com"
        existing_user_model.username = "testuser"
        existing_user_model.full_name = "Original Name"
        existing_user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user_model
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method
        user_repository._to_domain = MagicMock(return_value=updated_user)

        # Act
        result = await user_repository.update(user_id, updated_user)

        # Assert
        assert result == updated_user
        assert existing_user_model.full_name == "Updated Name"
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_user_model)

    async def test_delete_user_success(self, user_repository, mock_session):
        """Test successful user deletion."""
        # Arrange
        user_id = str(uuid4())

        existing_user_model = MagicMock()
        existing_user_model.id = user_id
        existing_user_model.email = "test@example.com"
        existing_user_model.username = "testuser"
        existing_user_model.full_name = "Test User"
        existing_user_model.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user_model
        mock_session.execute.return_value = mock_result

        # Act
        await user_repository.delete(user_id)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.delete.assert_called_once_with(existing_user_model)
        mock_session.commit.assert_called_once()

    async def test_list_all_users(self, user_repository, mock_session):
        """Test listing all users."""
        # Arrange
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
                is_active=False,
            ),
        ]

        user_models = [
            MagicMock(
                id=users[0].id,
                email="user1@example.com",
                username="user1",
                full_name="User One",
                is_active=True,
            ),
            MagicMock(
                id=users[1].id,
                email="user2@example.com",
                username="user2",
                full_name="User Two",
                is_active=False,
            ),
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = user_models

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Mock the _to_domain method to convert models to domain objects
        user_repository._to_domain = MagicMock(side_effect=users)

        # Act
        result = await user_repository.list_all()

        # Assert
        assert len(result) == 2
        assert result == users
        mock_session.execute.assert_called_once()
