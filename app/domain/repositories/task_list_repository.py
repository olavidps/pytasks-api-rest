"""TaskList repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.task_list import TaskList


class TaskListRepository(ABC):
    """TaskList repository interface for data access operations."""

    @abstractmethod
    async def create(self, task_list: TaskList) -> TaskList:
        """Create a new task list.

        Args:
            task_list: TaskList entity to create

        Returns:
            Created task list with generated ID
        """

    @abstractmethod
    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Get task list by id.

        Args:
            task_list_id: Unique identifier of the task list

        Returns:
            TaskList if found, None otherwise
        """

    @abstractmethod
    async def update(self, task_list: TaskList) -> TaskList:
        """Update task list.

        Args:
            task_list: TaskList entity with updated values

        Returns:
            Updated task list

        Raises:
            TaskListNotFoundError: If task list with given ID doesn't exist
        """

    @abstractmethod
    async def delete(self, task_list_id: UUID) -> bool:
        """Delete task list by id.

        Args:
            task_list_id: Unique identifier of the task list to delete

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def get_by_owner_id(
        self, owner_id: UUID, is_active: bool = True, skip: int = 0, limit: int = 100
    ) -> List[TaskList]:
        """Get task lists by owner id.

        Args:
            owner_id: ID of the user who owns the task lists
            is_active: Filter by active/inactive status
            skip: Number of task lists to skip for pagination
            limit: Maximum number of task lists to return

        Returns:
            List of task lists owned by the user
        """

    @abstractmethod
    async def exists(self, task_list_id: UUID) -> bool:
        """Check if task list exists.

        Args:
            task_list_id: ID of the task list to check

        Returns:
            True if task list exists, False otherwise
        """
