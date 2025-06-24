"""Create task list use case module."""

from app.api.schemas import TaskListCreate
from app.application.services.task_list_validation_service import (
    TaskListValidationService,
)
from app.domain.models.task_list import TaskList
from app.domain.services.task_list_domain_service import TaskListDomainService


class CreateTaskListUseCase:
    """Use case for creating a new task list."""

    def __init__(
        self,
        task_list_domain_service: TaskListDomainService,
        task_list_validation_service: TaskListValidationService,
    ):
        self._task_list_domain_service = task_list_domain_service
        self._task_list_validation_service = task_list_validation_service

    async def execute(self, task_list_data: TaskListCreate) -> TaskList:
        """Execute the create task list use case."""
        task_list_kwargs = {
            "name": task_list_data.name,
            "description": task_list_data.description,
        }

        if "owner_id" in task_list_data:
            await self._task_list_validation_service.validate_owner_exists(
                task_list_data.owner_id
            )
            task_list_kwargs["owner_id"] = task_list_data.owner_id

        task_list = TaskList(**task_list_kwargs)
        created_task_list = await self._task_list_domain_service.create_task_list(
            task_list
        )
        return created_task_list
