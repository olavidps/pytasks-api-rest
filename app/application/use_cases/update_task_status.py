"""Update task status use case module."""

from uuid import UUID

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepository


class UpdateTaskStatusUseCase:
    """Use case for updating task status.

    This use case handles the business logic for task status updates,
    using domain methods for status transitions.
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: UUID, new_status: TaskStatus) -> Task:
        """Execute task status update use case.

        Args:
            task_id: ID of the task to update
            new_status: New status for the task

        Returns:
            Updated task entity

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValueError: If status transition is invalid
        """
        # Get existing task
        existing_task = await self.task_repository.get_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        # Apply status change using domain methods
        if new_status == TaskStatus.PENDING:
            updated_task = existing_task.mark_as_pending()
        elif new_status == TaskStatus.IN_PROGRESS:
            updated_task = existing_task.mark_as_in_progress()
        elif new_status == TaskStatus.COMPLETED:
            updated_task = existing_task.mark_as_completed()
        else:
            raise ValueError(f"Invalid task status: {new_status}")

        # Persist the changes
        return await self.task_repository.update(updated_task)
