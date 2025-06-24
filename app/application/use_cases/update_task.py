"""Update task use case module."""

from typing import Optional
from uuid import UUID

from app.application.services.task_validation_service import TaskValidationService
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task
from app.domain.repositories.task_repository import TaskRepository


class UpdateTaskUseCase:
    """Use case for updating task information.

    This use case handles the business logic for task updates,
    including validation and persistence using domain methods.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_validation_service: TaskValidationService,
    ):
        self.task_repository = task_repository
        self.task_validation_service = task_validation_service

    async def execute(
        self, task_id: UUID, task_data: Task, updater_user_id: Optional[UUID] = None
    ) -> Task:
        """Execute task update use case.

        Args:
            task_id: ID of the task to update
            task_data: Updated task data
            updater_user_id: ID of the user updating the task

        Returns:
            Updated task entity

        Raises:
            TaskNotFoundError: If task doesn't exist
            UserNotFoundError: If assigned user doesn't exist or is inactive
            ValueError: If task data is invalid
        """
        # Check if task exists
        existing_task = await self.task_repository.get_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        # Validate task update
        await self.task_validation_service.validate_task_update(
            task_id, task_data, updater_user_id
        )

        # Update the task
        updated_task = await self.task_repository.update(task_data)
        return updated_task
