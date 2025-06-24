"""Task repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.task import Task, TaskPriority, TaskStatus


class TaskRepository(ABC):
    """Task repository interface for data access operations."""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Create a new task.

        Args:
            task: Task entity to create

        Returns:
            Created task with generated ID
        """

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by id.

        Args:
            task_id: Unique identifier of the task

        Returns:
            Task if found, None otherwise
        """

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update task.

        Args:
            task: Task entity with updated values

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """Delete task by id.

        Args:
            task_id: Unique identifier of the task to delete

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def get_by_task_list_id(
        self,
        task_list_id: UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Task]:
        """Get tasks by task list id with optional filters.

        Args:
            task_list_id: ID of the task list to filter by
            status: Optional filter by task status
            priority: Optional filter by task priority
            limit: Maximum number of tasks to return
            skip: Number of tasks to skip for pagination

        Returns:
            List of tasks matching the criteria
        """

    @abstractmethod
    async def get_by_assigned_user_id(
        self,
        user_id: UUID,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Task]:
        """Get tasks assigned to a user.

        Args:
            user_id: ID of the user tasks are assigned to
            status: Optional filter by task status
            limit: Maximum number of tasks to return
            skip: Number of tasks to skip for pagination

        Returns:
            List of tasks assigned to the user
        """

    @abstractmethod
    async def count_by_task_list_id(
        self,
        task_list_id: UUID,
        status: Optional[TaskStatus] = None,
    ) -> int:
        """Count tasks in a task list.

        Args:
            task_list_id: ID of the task list to count tasks for
            status: Optional filter by task status

        Returns:
            Number of tasks in the list matching the criteria
        """

    @abstractmethod
    async def exists(self, task_id: UUID) -> bool:
        """Check if task exists.

        Args:
            task_id: ID of the task to check

        Returns:
            True if task exists, False otherwise
        """

    @abstractmethod
    async def get_paginated(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> tuple[List[Task], int]:
        """Get paginated tasks with optional filters.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply

        Returns:
            Tuple containing list of tasks and total count
        """
