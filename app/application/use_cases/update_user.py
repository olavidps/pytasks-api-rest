"""Update user use case module."""

from uuid import UUID

from app.api.schemas.user_schemas import UserUpdate
from app.application.services.user_validation_service import UserValidationService
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class UpdateUserUseCase:
    """Use case for updating user profile information.

    This use case handles the business logic for user updates,
    including validation and persistence using domain methods.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        user_validation_service: UserValidationService,
    ):
        self.user_repository = user_repository
        self.user_validation_service = user_validation_service

    async def execute(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Execute user update use case.

        Args:
            user_id: ID of the user to update
            user_data: User update data

        Returns:
            Updated user entity

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        # Get existing user
        existing_user = await self.user_repository.get_by_id(user_id)

        # Validate user availability (only validates changed fields)
        await self.user_validation_service.validate_user_availability(
            user_data, existing_user
        )

        # Use the domain entity's update_profile method (more pythonic)
        updated_user = existing_user.update_profile(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
        )

        # Update the user in repository
        return await self.user_repository.update(user_id, updated_user)
