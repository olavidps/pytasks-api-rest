"""Get task use case module."""

from typing import Optional
from uuid import UUID

from app.api.schemas.task_schemas import TaskListSummary, TaskWithRelations, UserSummary
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository


class GetTaskUseCase:
    """Use case for retrieving a task by ID."""

    def __init__(
        self,
        task_repository: TaskRepository,
        task_list_repository: TaskListRepository,
        user_repository: UserRepository,
    ):
        self.task_repository = task_repository
        self.task_list_repository = task_list_repository
        self.user_repository = user_repository

    async def execute(self, task_id: UUID) -> TaskWithRelations:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        task_list = await self.task_list_repository.get_by_id(task.task_list_id)
        if not task_list:
            # This should ideally not happen if referential integrity is maintained
            raise TaskNotFoundError(
                f"Task list with id {task.task_list_id} not found for task {task_id}"
            )

        assigned_user_summary: Optional[UserSummary] = None
        if task.assigned_user_id:
            assigned_user = await self.user_repository.get_by_id(task.assigned_user_id)
            if assigned_user:
                assigned_user_summary = UserSummary.model_validate(assigned_user)

        return TaskWithRelations(
            **task.model_dump(),
            task_list=TaskListSummary.model_validate(task_list),
            assigned_user=assigned_user_summary,
        )
