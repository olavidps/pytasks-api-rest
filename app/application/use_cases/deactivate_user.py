"""Deactivate user use case."""

from uuid import UUID

from app.domain.exceptions.user import UserNotFoundError
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class DeactivateUserUseCase:
    """Use case for deactivating a user account."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> User:
        """Deactivate a user account.

        Args:
            user_id: The ID of the user to deactivate

        Returns:
            The deactivated user

        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        # Check if user exists
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Deactivate user
        updated_user = await self.user_repository.update(user_id, {"is_active": False})
        return updated_user
