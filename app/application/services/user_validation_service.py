"""User validation service for application layer."""

from typing import Optional

from app.domain.exceptions import UserAlreadyExistsError
from app.domain.models.user import User
from app.domain.services.user_domain_service import UserDomainService


class UserValidationService:
    """Service to handle user validation logic at the application layer."""

    def __init__(self, user_domain_service: UserDomainService):
        self.user_domain_service = user_domain_service

    async def validate_user_availability(
        self, user_data: User, existing_user: Optional[User] = None
    ) -> None:
        """Validate that username and email are available for use.

        Args:
            user_data: User data to validate
            existing_user: Current user data (for updates), None for new users

        Raises:
            UserAlreadyExistsError: If username or email is already taken
            ValueError: If username format is invalid
        """
        await self._validate_email_availability(user_data.email, existing_user)
        await self._validate_username_availability(user_data.username, existing_user)

    async def _validate_email_availability(
        self, email: str, existing_user: Optional[User] = None
    ) -> None:
        """Validate email availability."""
        # Skip validation if email hasn't changed
        if existing_user and email == existing_user.email:
            return

        is_available = await self.user_domain_service.validate_email_availability(
            email=email
        )
        if not is_available:
            raise UserAlreadyExistsError("Email", email)

    async def _validate_username_availability(
        self, username: str, existing_user: Optional[User] = None
    ) -> None:
        """Validate username availability."""
        # Skip validation if username hasn't changed
        if existing_user and username == existing_user.username:
            return

        is_available = await self.user_domain_service.validate_username_availability(
            username=username
        )
        if not is_available:
            raise UserAlreadyExistsError("Username", username)
