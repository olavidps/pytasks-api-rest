"""Task domain service for complex business logic."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.domain.models.task import Task, TaskStatus
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository


class TaskDomainService:
    """Domain service for task-related business logic that involves multiple entities or complex operations."""

    def __init__(
        self,
        task_repository: TaskRepository,
        task_list_repository: TaskListRepository,
        user_repository: UserRepository,
    ):
        self._task_repository = task_repository
        self._task_list_repository = task_list_repository
        self._user_repository = user_repository

    async def validate_task_assignment(
        self, task_id: UUID, assigned_user_id: Optional[UUID]
    ) -> bool:
        """Validate if a task can be assigned to a specific user.

        Args:
            task_id: The ID of the task to assign
            assigned_user_id: The ID of the user to assign the task to

        Returns:
            True if the assignment is valid, False otherwise
        """
        if assigned_user_id is None:
            return True  # Unassigning is always valid

        # Check if user exists and is active
        user = await self._user_repository.get_by_id(assigned_user_id)
        if not user or not user.is_active:
            return False

        return True

    async def validate_task_list_ownership(
        self, task_list_id: UUID, user_id: UUID
    ) -> bool:
        """Validate if a user owns or has access to a task list.

        Args:
            task_list_id: The ID of the task list
            user_id: The ID of the user

        Returns:
            True if the user has access to the task list, False otherwise
        """
        task_list = await self._task_list_repository.get_by_id(task_list_id)
        if not task_list or not task_list.is_active:
            return False

        # For now, only the owner can create tasks in the list
        # This can be extended to support shared lists in the future
        return task_list.owner_id == user_id

    async def can_task_be_deleted(self, task_id: UUID) -> tuple[bool, str]:
        """Check if a task can be safely deleted.

        Args:
            task_id: The ID of the task to check

        Returns:
            Tuple of (can_delete: bool, reason: str)
        """
        task = await self._task_repository.get_by_id(task_id)
        if not task:
            return False, "Task not found"

        # Business rule: Completed tasks older than 30 days should be archived instead of deleted
        if task.status == TaskStatus.COMPLETED and task.completed_at:
            days_since_completion = (
                datetime.now(timezone.utc) - task.completed_at
            ).days
            if days_since_completion > 30:
                return (
                    False,
                    "Completed tasks older than 30 days should be archived instead of deleted",
                )

        return True, "Task can be deleted"

    async def get_overdue_tasks_for_user(self, user_id: UUID) -> List[Task]:
        """Get all overdue tasks assigned to a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of overdue tasks
        """
        tasks = await self._task_repository.get_by_assigned_user_id(user_id)
        return [task for task in tasks if task.is_overdue]

    async def calculate_task_completion_rate(
        self, task_list_id: UUID, user_id: Optional[UUID] = None
    ) -> float:
        """Calculate the completion rate for tasks in a task list.

        Args:
            task_list_id: The ID of the task list
            user_id: Optional user ID to filter tasks by assignee

        Returns:
            Completion rate as a percentage (0.0 to 100.0)
        """
        if user_id:
            all_tasks = await self._task_repository.get_by_assigned_user_id(user_id)
            # Filter by task list
            tasks = [task for task in all_tasks if task.task_list_id == task_list_id]
        else:
            tasks = await self._task_repository.get_by_task_list_id(task_list_id)

        if not tasks:
            return 0.0

        completed_tasks = [
            task for task in tasks if task.status == TaskStatus.COMPLETED
        ]
        return (len(completed_tasks) / len(tasks)) * 100.0

    async def validate_due_date_consistency(self, task: Task) -> bool:
        """Validate that the due date is consistent with task status.

        Args:
            task: The task to validate

        Returns:
            True if due date is consistent, False otherwise
        """
        if task.status == TaskStatus.COMPLETED:
            # Completed tasks should have completion date before or equal to due date
            if task.due_date and task.completed_at:
                return task.completed_at <= task.due_date

        return True
