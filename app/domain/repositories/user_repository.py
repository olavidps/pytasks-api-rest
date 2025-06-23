"""User repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.user import User


class UserRepository(ABC):
    """User repository interface for data access operations."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user with generated ID
        """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by id.

        Args:
            user_id: Unique identifier of the user

        Returns:
            User if found, None otherwise
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address of the user

        Returns:
            User if found, None otherwise
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username of the user

        Returns:
            User if found, None otherwise
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user.

        Args:
            user: User entity with updated values

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user with given ID doesn't exist
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by id.

        Args:
            user_id: Unique identifier of the user to delete

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
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

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """Check if user exists.

        Args:
            user_id: ID of the user to check

        Returns:
            True if user exists, False otherwise
        """

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists.

        Args:
            username: Username to check

        Returns:
            True if username exists, False otherwise
        """

    @abstractmethod
    async def get_paginated(
        self, offset: int = 0, limit: int = 20, filters: Optional[dict] = None
    ) -> tuple[List[User], int]:
        """Get paginated users with optional filtering.

        Args:
            offset: Number of users to skip
            limit: Maximum number of users to return
            filters: Optional dictionary of filters (search, is_active)

        Returns:
            Tuple of (users list, total count)
        """
