"""Task list domain service module."""

from typing import List, Optional
from uuid import UUID

from app.domain.models.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository


class TaskListDomainService:
    """Domain service for managing task lists."""

    def __init__(self, task_list_repository: TaskListRepository):
        self._task_list_repository = task_list_repository

    async def create_task_list(self, task_list: TaskList) -> TaskList:
        """Create a new task list."""
        return await self._task_list_repository.create(task_list)

    async def get_task_list_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Get a task list by its ID."""
        return await self._task_list_repository.get_by_id(task_list_id)

    async def get_paginated_task_lists(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> tuple[List[TaskList], int]:
        """Get paginated task lists with optional filters."""
        return await self._task_list_repository.get_paginated(offset, limit, filters)

    async def delete_task_list(self, task_list_id: UUID) -> None:
        """Delete a task list."""
        await self._task_list_repository.delete(task_list_id)

    async def task_list_exists(self, task_list_id: UUID) -> bool:
        """Check if a task list exists."""
        return await self._task_list_repository.exists(task_list_id)
