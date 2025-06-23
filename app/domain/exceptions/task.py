"""Task-related domain exceptions."""

from uuid import UUID

from .base import NotFoundError


class TaskNotFoundError(NotFoundError):
    """Task not found error exception."""

    def __init__(self, task_id: UUID):
        """Initialize task not found error.

        Args:
            task_id: ID of task that was not found
        """
        super().__init__("Task", task_id)
