"""Create user use case module."""

from app.application.services.user_validation_service import UserValidationService
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    """Use case for creating new users.

    This use case handles the business logic for user creation,
    including validation and persistence.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        user_validation_service: UserValidationService,
    ):
        self.user_repository = user_repository
        self.user_validation_service = user_validation_service

    async def execute(self, user_data: User) -> User:
        """Execute user creation use case.

        Args:
            user_data: User entity with the data to create

        Returns:
            Created user entity

        Raises:
            UserAlreadyExistsError: If user with same email or username exists
        """
        # Validate user availability
        await self.user_validation_service.validate_user_availability(user_data)

        # Create the user
        created_user = await self.user_repository.create(user_data)
        return created_user
