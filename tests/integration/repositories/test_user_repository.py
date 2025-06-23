"""Unit tests for UserRepository implementation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.domain.models.user import User
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestUserRepositoryImpl:
    """Test cases for UserRepositoryImpl."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, isolated_db_session: AsyncSession):
        """Test successful user creation."""
        from datetime import datetime
        from uuid import uuid4

        repo = UserRepositoryImpl(isolated_db_session)

        # Create user directly in test
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        created_user = await repo.create(user)

        assert created_user.id == user.id
        assert created_user.email == user.email
        assert created_user.username == user.username
        assert created_user.full_name == user.full_name
        assert created_user.is_active == user.is_active

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, isolated_db_session: AsyncSession, sample_user: User, sample_user_2: User
    ):
        """Test user creation with duplicate email raises exception."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create first user
        await repo.create(sample_user)

        # Try to create second user with same email
        duplicate_user = sample_user_2.model_copy(update={"email": sample_user.email})

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await repo.create(duplicate_user)

        assert "email" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(
        self, isolated_db_session: AsyncSession, sample_user: User, sample_user_2: User
    ):
        """Test user creation with duplicate username raises exception."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create first user
        await repo.create(sample_user)

        # Try to create second user with same username
        duplicate_user = sample_user_2.model_copy(
            update={"username": sample_user.username}
        )

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await repo.create(duplicate_user)

        assert "username" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_existing_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test getting existing user by ID."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create user
        await repo.create(sample_user)

        # Get user by ID
        found_user = await repo.get_by_id(sample_user.id)

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test getting nonexistent user by ID returns None."""
        repo = UserRepositoryImpl(isolated_db_session)

        found_user = await repo.get_by_id(sample_user.id)

        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_by_email_existing_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test getting existing user by email."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create user
        await repo.create(sample_user)

        # Get user by email
        found_user = await repo.get_by_email(sample_user.email)

        assert found_user is not None
        assert found_user.email == sample_user.email
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_by_email_nonexistent_user(
        self, isolated_db_session: AsyncSession
    ):
        """Test getting nonexistent user by email returns None."""
        repo = UserRepositoryImpl(isolated_db_session)

        found_user = await repo.get_by_email("nonexistent@example.com")

        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_by_username_existing_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test getting existing user by username."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create user
        await repo.create(sample_user)

        # Get user by username
        found_user = await repo.get_by_username(sample_user.username)

        assert found_user is not None
        assert found_user.username == sample_user.username
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_by_username_nonexistent_user(
        self, isolated_db_session: AsyncSession
    ):
        """Test getting nonexistent user by username returns None."""
        repo = UserRepositoryImpl(isolated_db_session)

        found_user = await repo.get_by_username("nonexistent")

        assert found_user is None

    @pytest.mark.asyncio
    async def test_update_user_success(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test successful user update."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create user
        await repo.create(sample_user)

        # Update user
        updated_user = sample_user.update_profile(
            username="updated_username",
            full_name="Updated Name",
            email="updated@example.com",
        )

        result = await repo.update(updated_user)

        assert result.username == "updated_username"
        assert result.full_name == "Updated Name"
        assert result.email == "updated@example.com"
        assert result.id == sample_user.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test updating nonexistent user raises exception."""
        repo = UserRepositoryImpl(isolated_db_session)

        with pytest.raises(UserNotFoundError):
            await repo.update(sample_user)

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test successful user deletion."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create user
        await repo.create(sample_user)

        # Delete user
        result = await repo.delete(sample_user.id)

        assert result is True

        # Verify user is deleted
        found_user = await repo.get_by_id(sample_user.id)
        assert found_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(
        self, isolated_db_session: AsyncSession, sample_user: User
    ):
        """Test deleting nonexistent user returns False."""
        repo = UserRepositoryImpl(isolated_db_session)

        result = await repo.delete(sample_user.id)

        assert result is False

    @pytest.mark.asyncio
    async def test_list_all_users(
        self, isolated_db_session: AsyncSession, sample_user: User, sample_user_2: User
    ):
        """Test listing all users with pagination."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create users
        await repo.create(sample_user)
        await repo.create(sample_user_2)

        # List all users
        users = await repo.list_all()

        assert len(users) == 2
        user_ids = {user.id for user in users}
        assert sample_user.id in user_ids
        assert sample_user_2.id in user_ids

    @pytest.mark.asyncio
    async def test_list_all_users_with_pagination(
        self, isolated_db_session: AsyncSession, sample_user: User, sample_user_2: User
    ):
        """Test listing users with pagination parameters."""
        repo = UserRepositoryImpl(isolated_db_session)

        # Create users
        await repo.create(sample_user)
        await repo.create(sample_user_2)

        # List with limit
        users = await repo.list_all(skip=0, limit=1)

        assert len(users) == 1

        # List with skip
        users = await repo.list_all(skip=1, limit=10)

        assert len(users) == 1
