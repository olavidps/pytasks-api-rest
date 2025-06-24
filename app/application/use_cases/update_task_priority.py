"""Update task priority use case module."""

from uuid import UUID

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskPriority
from app.domain.repositories.task_repository import TaskRepository


class UpdateTaskPriorityUseCase:
    """Use case for updating task priority.

    This use case handles the business logic for task priority updates,
    using domain methods for priority changes.
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: UUID, new_priority: TaskPriority) -> Task:
        """Execute task priority update use case.

        Args:
            task_id: ID of the task to update
            new_priority: New priority for the task

        Returns:
            Updated task entity

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValueError: If priority value is invalid
        """
        # Get existing task
        existing_task = await self.task_repository.get_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        # Validate priority value
        if new_priority not in TaskPriority:
            raise ValueError(f"Invalid task priority: {new_priority}")

        # Apply priority change using domain method
        updated_task = existing_task.update_priority(new_priority)

        # Persist the changes
        return await self.task_repository.update(updated_task)
