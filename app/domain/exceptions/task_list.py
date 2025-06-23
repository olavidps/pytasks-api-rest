"""TaskList-related domain exceptions."""

from uuid import UUID

from .base import AlreadyExistsError, NotFoundError


class TaskListNotFoundError(NotFoundError):
    """TaskList not found error exception."""

    def __init__(self, task_list_id: UUID):
        """Initialize task list not found error.

        Args:
            task_list_id: ID of task list that was not found
        """
        super().__init__("TaskList", task_list_id)


class TaskListAlreadyExistsError(AlreadyExistsError):
    """TaskList already exists error exception."""

    def __init__(self, name: str, owner_id: UUID):
        """Initialize task list already exists error.

        Args:
            name: Name of the task list that already exists
            owner_id: ID of the owner of the task list
        """
        super().__init__("TaskList", "name", name)
        self.details["owner_id"] = str(owner_id)
        # Override the default message for more context
        self.message = f"TaskList with name '{name}' already exists for user {owner_id}"
