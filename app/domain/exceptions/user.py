"""User-related domain exceptions."""

from uuid import UUID

from .base import AlreadyExistsError, DomainException, NotFoundError


class UserNotFoundError(NotFoundError):
    """User not found error exception."""

    def __init__(self, user_id: UUID):
        """Initialize user not found error.

        Args:
            user_id: ID of user that was not found
        """
        super().__init__("User", user_id)


class UserAlreadyExistsError(AlreadyExistsError):
    """User already exists error exception."""

    def __init__(self, field: str, value: str):
        """Initialize user already exists error.

        Args:
            field: Field that has the duplicate value (e.g. email, username)
            value: Value that caused the duplicate error
        """
        super().__init__("User", field, value)


class UnauthorizedOperationError(DomainException):
    """Unauthorized operation error exception."""

    def __init__(self, operation: str, resource: str):
        """Initialize unauthorized operation error.

        Args:
            operation: Operation that was attempted (e.g. update, delete)
            resource: Resource that was accessed (e.g. task, task_list)
        """
        message = f"Unauthorized to perform '{operation}' on '{resource}'"
        super().__init__(message, {"operation": operation, "resource": resource})
