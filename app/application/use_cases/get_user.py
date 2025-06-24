"""Get user use case module."""

from uuid import UUID

from app.domain.exceptions.user import UserNotFoundError
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    """Use case for retrieving a user by ID."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> User:
        """Get a user by ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            The user

        Raises:
            UserNotFoundError: If the user doesn't exist
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user
