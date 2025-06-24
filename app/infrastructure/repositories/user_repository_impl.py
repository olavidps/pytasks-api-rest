"""User repository implementation."""

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user import UserNotFoundError
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """User repository implementation using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: Database session
        """
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user with generated ID
        """
        user_model = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)

        return self._to_domain(user_model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by id.

        Args:
            user_id: Unique identifier of the user

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return self._to_domain(user_model)

    async def get_by_email(self, email: str) -> User:
        """Get user by email.

        Args:
            email: Email address of the user

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with given email doesn't exist
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundError(f"User with email {email} not found")

        return self._to_domain(user_model)

    async def get_by_username(self, username: str) -> User:
        """Get user by username.

        Args:
            username: Username of the user

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with given username doesn't exist
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundError(f"User with username {username} not found")

        return self._to_domain(user_model)

    async def update(self, user_id: str, user: User) -> User:
        """Update user.

        Args:
            user: User entity with updated values

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user with given ID doesn't exist
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundError(user.id)

        # Update fields
        user_model.email = user.email
        user_model.username = user.username
        user_model.full_name = user.full_name
        user_model.is_active = user.is_active
        user_model.updated_at = user.updated_at
        user_model.last_login = user.last_login

        await self.session.commit()
        await self.session.refresh(user_model)

        return self._to_domain(user_model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user by id.

        Args:
            user_id: Unique identifier of the user

        Returns:
            True if user was deleted, False if not found
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        await self.session.delete(user_model)
        await self.session.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of users
        """
        result = await self.session.execute(select(UserModel).offset(skip).limit(limit))
        user_models = result.scalars().all()

        return [self._to_domain(user_model) for user_model in user_models]

    async def get_all(
        self, is_active: Optional[bool] = None, limit: int = 100, offset: int = 0
    ) -> List[User]:
        """Get all users with optional filtering.

        Args:
            is_active: Optional filter by active status
            limit: Maximum number of users to return
            offset: Number of users to skip for pagination

        Returns:
            List of users matching the criteria
        """
        query = select(UserModel)

        if is_active is not None:
            query = query.where(UserModel.is_active == is_active)

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        user_models = result.scalars().all()

        return [self._to_domain(user_model) for user_model in user_models]

    async def exists(self, user_id: UUID) -> bool:
        """Check if user exists.

        Args:
            user_id: ID of the user to check

        Returns:
            True if user exists, False otherwise
        """
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none() is not None

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists.

        Args:
            username: Username to check

        Returns:
            True if username exists, False otherwise
        """
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def get_paginated(
        self, offset: int = 0, limit: int = 20, filters: Optional[Dict] = None
    ) -> tuple[List[User], int]:
        """Get paginated users with optional filtering.

        Args:
            offset: Number of users to skip
            limit: Maximum number of users to return
            filters: Optional dictionary of filters (search, is_active)

        Returns:
            Tuple of (users list, total count)
        """
        # Build base query
        query = select(UserModel)
        count_query = select(func.count(UserModel.id))

        # Apply filters if provided
        if filters:
            # Filter by active status
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.where(UserModel.is_active == filters["is_active"])
                count_query = count_query.where(
                    UserModel.is_active == filters["is_active"]
                )

            # Filter by search term (search in username, email, or full_name)
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                search_condition = or_(
                    UserModel.username.ilike(search_term),
                    UserModel.email.ilike(search_term),
                    UserModel.full_name.ilike(search_term),
                )
                query = query.where(search_condition)
                count_query = count_query.where(search_condition)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and get results
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        user_models = result.scalars().all()

        # Convert to domain entities
        users = [self._to_domain(user_model) for user_model in user_models]

        return users, total

    def _to_domain(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity.

        Args:
            user_model: SQLAlchemy user model

        Returns:
            User domain entity
        """
        return User(
            id=user_model.id,
            email=user_model.email,
            username=user_model.username,
            full_name=user_model.full_name,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login=user_model.last_login,
        )
