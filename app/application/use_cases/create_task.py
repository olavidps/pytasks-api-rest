"""Create task use case module."""

from typing import Optional
from uuid import UUID

from app.application.services.task_validation_service import TaskValidationService
from app.domain.models.task import Task
from app.domain.repositories.task_repository import TaskRepository


class CreateTaskUseCase:
    """Use case for creating new tasks.

    This use case handles the business logic for task creation,
    including validation and persistence.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_validation_service: TaskValidationService,
    ):
        self.task_repository = task_repository
        self.task_validation_service = task_validation_service

    async def execute(
        self, task_data: Task, creator_user_id: Optional[UUID] = None
    ) -> Task:
        """Execute task creation use case.

        Args:
            task_data: Task entity with the data to create
            creator_user_id: ID of the user creating the task

        Returns:
            Created task entity

        Raises:
            TaskListNotFoundError: If task list doesn't exist or user doesn't have access
            UserNotFoundError: If assigned user doesn't exist or is inactive
            ValueError: If task data is invalid
        """
        # Validate task creation
        await self.task_validation_service.validate_task_creation(
            task_data, creator_user_id
        )

        # Create the task
        created_task = await self.task_repository.create(task_data)
        return created_task
