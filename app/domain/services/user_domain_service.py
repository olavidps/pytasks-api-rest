"""User domain service for complex business logic."""

from typing import Optional

from app.domain.exceptions.user import UserNotFoundError
from app.domain.repositories.user_repository import UserRepository


class UserDomainService:
    """Domain service for user-related business logic that involves multiple entities or complex operations."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def validate_username_availability(
        self, username: str, exclude_user_id: Optional[str] = None
    ) -> bool:
        """Validate if a username is available based on business rules.

        Args:
            username: The username to validate.
            exclude_user_id: Optional user ID to exclude from the check (for updates).

        Returns:
            True if the username is available, False otherwise.
        """
        # Rule 1: Username must be at least 3 characters long
        if len(username) < 3:
            return False

        # Rule 2: Username must be alphanumeric (can contain underscores, but not at the start)
        if not username.replace("_", "").isalnum() or username.startswith("_"):
            return False

        # Rule 3: Check against existing usernames in the repository
        try:
            existing_user = await self._user_repository.get_by_username(
                username
            )  # Use get_by_username
            if existing_user and (
                exclude_user_id is None or str(existing_user.id) != exclude_user_id
            ):
                return False
        except UserNotFoundError:
            # User not found, username is available
            pass

        return True

    async def validate_email_availability(
        self, email: str, exclude_user_id: Optional[str] = None
    ) -> bool:
        """Validate if an email is available.

        Args:
            email: The email to validate.
            exclude_user_id: Optional user ID to exclude from the check (for updates).

        Returns:
            True if the email is available, False otherwise.
        """
        try:
            existing_user = await self._user_repository.get_by_email(email)
            if existing_user and (
                exclude_user_id is None or str(existing_user.id) != exclude_user_id
            ):
                return False
        except UserNotFoundError:
            # Email not found, email is available
            pass

        return True

    async def can_user_be_deleted(self, user_id: str) -> tuple[bool, str]:
        """Check if a user can be safely deleted.

        Args:
            user_id: The ID of the user to check

        Returns:
            Tuple of (can_delete: bool, reason: str)
        """
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return False, "User not found"

        # Business rule: Cannot delete user if they own active task lists
        # This would require checking with TaskListRepository
        # For now, we'll assume it's always safe to delete
        # In a real implementation, you'd inject TaskListRepository and check

        return True, "User can be safely deleted"
