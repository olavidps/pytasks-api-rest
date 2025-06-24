"""Update task assignment use case module."""

from typing import Optional
from uuid import UUID

from app.application.services.task_validation_service import TaskValidationService
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task
from app.domain.repositories.task_repository import TaskRepository


class UpdateTaskAssignmentUseCase:
    """Use case for updating task assignment.

    This use case handles the business logic for task assignment updates,
    including validation and persistence using domain methods.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_validation_service: TaskValidationService,
    ):
        self.task_repository = task_repository
        self.task_validation_service = task_validation_service

    async def execute(self, task_id: UUID, assigned_user_id: Optional[UUID]) -> Task:
        """Execute task assignment update use case.

        Args:
            task_id: ID of the task to update
            assigned_user_id: ID of the user to assign the task to (None to unassign)

        Returns:
            Updated task entity

        Raises:
            TaskNotFoundError: If task doesn't exist
            UserNotFoundError: If assigned user doesn't exist or is inactive
        """
        # Get existing task
        existing_task = await self.task_repository.get_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        # Validate task assignment
        await self.task_validation_service.validate_task_assignment_update(
            task_id, assigned_user_id
        )

        # Apply assignment change using domain method
        if assigned_user_id is not None:
            updated_task = existing_task.assign_to_user(assigned_user_id)
        else:
            # Unassign task
            updated_task = existing_task.unassign()

        # Persist the changes
        return await self.task_repository.update(updated_task)
