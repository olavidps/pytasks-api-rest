"""Update task list use case module."""

from uuid import UUID

from app.application.services.task_list_validation_service import (
    TaskListValidationService,
)
from app.domain.models.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository


class UpdateTaskListUseCase:
    """Use case for updating an existing task list."""

    def __init__(
        self,
        task_list_repository: TaskListRepository,
        task_list_validation_service: TaskListValidationService,
    ):
        self._task_list_repository = task_list_repository
        self._task_list_validation_service = task_list_validation_service

    async def execute(self, task_list_id: UUID, task_list_data: TaskList) -> TaskList:
        """Execute the update task list use case."""
        await self._task_list_validation_service.validate_task_list_exists(task_list_id)

        if task_list_data.owner_id:
            await self._task_list_validation_service.validate_owner_exists(
                task_list_data.owner_id
            )

        updated_task_list = await self._task_list_repository.update(
            task_list_id, task_list_data
        )
        return updated_task_list
