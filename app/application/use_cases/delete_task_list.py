"""Delete task list use case module."""

from uuid import UUID

from app.application.services.task_list_validation_service import (
    TaskListValidationService,
)
from app.domain.services.task_list_domain_service import TaskListDomainService


class DeleteTaskListUseCase:
    """Use case for deleting a task list."""

    def __init__(
        self,
        task_list_domain_service: TaskListDomainService,
        task_list_validation_service: TaskListValidationService,
    ):
        self._task_list_domain_service = task_list_domain_service
        self._task_list_validation_service = task_list_validation_service

    async def execute(self, task_list_id: UUID) -> None:
        """Execute the delete task list use case."""
        await self._task_list_validation_service.validate_task_list_exists(task_list_id)
        await self._task_list_domain_service.delete_task_list(task_list_id)
