"""Base domain exceptions."""

from typing import Any, Dict, Optional
from uuid import UUID


class DomainException(Exception):
    """Base domain exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize domain exception.

        Args:
            message: Exception message
            details: Additional details about the exception
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(DomainException):
    """Validation error exception."""


class NotFoundError(DomainException):
    """Entity not found error exception."""

    def __init__(self, entity_type: str, entity_id: UUID):
        """Initialize not found error.

        Args:
            entity_type: Type of entity that was not found
            entity_id: ID of entity that was not found
        """
        message = f"{entity_type} with id {entity_id} not found"
        super().__init__(
            message, {"entity_type": entity_type, "entity_id": str(entity_id)}
        )


class AlreadyExistsError(DomainException):
    """Entity already exists error exception."""

    def __init__(self, entity_type: str, field: str, value: Any):
        """Initialize already exists error.

        Args:
            entity_type: Type of entity that already exists
            field: Field that has the duplicate value
            value: Value that caused the duplicate error
        """
        message = f"{entity_type} with {field} '{value}' already exists"
        super().__init__(
            message, {"entity_type": entity_type, "field": field, "value": str(value)}
        )
