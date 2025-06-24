"""Get tasks use case module."""

from typing import Dict, List, Tuple

from app.api.schemas import PaginationParams
from app.domain.models.task import Task
from app.domain.repositories.task_repository import TaskRepository


class GetTasksUseCase:
    """Use case for retrieving paginated tasks with optional filtering."""

    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    async def execute(
        self,
        pagination: PaginationParams,
        filters: Dict[str, any],
    ) -> Tuple[List[Task], int]:
        """Execute the get tasks use case.

        Args:
            pagination: Pagination parameters
            filters: Filter parameters

        Returns:
            Tuple containing list of tasks and total count

        Raises:
            ValueError: If pagination parameters are invalid
        """
        if pagination.size <= 0:
            raise ValueError("Page size must be greater than 0")
        if pagination.page < 1:
            raise ValueError("Page number must be greater than 0")

        # Get paginated results from repository
        tasks, total = await self._task_repository.get_paginated(
            offset=(pagination.page - 1) * pagination.size,
            limit=pagination.size,
            filters=filters,
        )

        return tasks, total
