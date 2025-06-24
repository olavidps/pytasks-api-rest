"""Get task list use case module."""

from typing import Optional
from uuid import UUID

from app.api.schemas import (
    PaginatedTaskListResponse,
    TaskListResponse,
    TaskListWithStats,
)
from app.application.services.task_list_validation_service import (
    TaskListValidationService,
)
from app.domain.services.task_list_domain_service import TaskListDomainService


class GetTaskListUseCase:
    """Use case for retrieving task lists."""

    def __init__(
        self,
        task_list_domain_service: TaskListDomainService,
        task_list_validation_service: TaskListValidationService,
    ):
        self._task_list_domain_service = task_list_domain_service
        self._task_list_validation_service = task_list_validation_service

    async def get_by_id(self, task_list_id: UUID) -> TaskListWithStats:
        """Get a task list by its ID."""
        await self._task_list_validation_service.validate_task_list_exists(task_list_id)
        task_list = await self._task_list_domain_service.get_task_list_by_id(
            task_list_id
        )

        # Calculate task statistics
        total_tasks = len(task_list.tasks)
        completed_tasks = sum(1 for task in task_list.tasks if task.is_completed)
        pending_tasks = sum(
            1
            for task in task_list.tasks
            if not task.is_completed and task.status != "in_progress"
        )
        in_progress_tasks = sum(
            1 for task in task_list.tasks if task.status == "in_progress"
        )
        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        return TaskListWithStats.model_validate(
            task_list.model_dump()
            | {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_percentage": completion_percentage,
            }
        )

    async def get_paginated(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        page: int = 1,
        size: int = 100,
    ) -> PaginatedTaskListResponse:
        """Get paginated task lists with optional filters."""
        task_lists, total = (
            await self._task_list_domain_service.get_paginated_task_lists(
                offset, limit, filters
            )
        )
        task_list_responses = [TaskListResponse.model_validate(tl) for tl in task_lists]
        return PaginatedTaskListResponse.create(
            items=task_list_responses, page=page, size=size, total=total
        )
