"""Delete user use case module."""

from uuid import UUID

from app.domain.exceptions.user import UserNotFoundError
from app.domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    """Use case for deleting a user account."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> None:
        """Delete a user account.

        Args:
            user_id: The ID of the user to delete

        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        # Check if user exists
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Delete user
        await self.user_repository.delete(user_id)
