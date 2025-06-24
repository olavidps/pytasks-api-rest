"""Delete task use case module."""

from uuid import UUID

from app.application.services.task_validation_service import TaskValidationService
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.repositories.task_repository import TaskRepository


class DeleteTaskUseCase:
    """Use case for deleting tasks.

    This use case handles the business logic for task deletion,
    including validation and persistence.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        task_validation_service: TaskValidationService,
    ):
        self.task_repository = task_repository
        self.task_validation_service = task_validation_service

    async def execute(self, task_id: UUID) -> None:
        """Execute task deletion use case.

        Args:
            task_id: ID of the task to delete

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValueError: If task cannot be deleted due to business rules
        """
        # Validate task deletion
        await self.task_validation_service.validate_task_deletion(task_id)

        # Delete the task
        deleted = await self.task_repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
