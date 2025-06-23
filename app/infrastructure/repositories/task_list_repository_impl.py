"""TaskList repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.models.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository
from app.infrastructure.database.models.task_list import TaskListModel


class TaskListRepositoryImpl(TaskListRepository):
    """TaskList repository implementation using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: Database session
        """
        self.session = session

    async def create(self, task_list: TaskList) -> TaskList:
        """Create a new task list.

        Args:
            task_list: TaskList entity to create

        Returns:
            Created task list with generated ID
        """
        # Create new task list model
        task_list_model = TaskListModel(
            id=task_list.id,
            name=task_list.name,
            description=task_list.description,
            owner_id=task_list.owner_id,
            is_active=task_list.is_active,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
        )

        self.session.add(task_list_model)
        await self.session.commit()
        await self.session.refresh(task_list_model)

        return self._to_domain(task_list_model)

    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Get task list by id.

        Args:
            task_list_id: Unique identifier of the task list

        Returns:
            TaskList if found, None otherwise
        """
        result = await self.session.execute(
            select(TaskListModel).where(TaskListModel.id == task_list_id)
        )
        task_list_model = result.scalar_one_or_none()

        if task_list_model is None:
            return None

        return self._to_domain(task_list_model)

    async def update(self, task_list: TaskList) -> TaskList:
        """Update task list.

        Args:
            task_list: TaskList entity with updated values

        Returns:
            Updated task list

        Raises:
            TaskListNotFoundError: If task list with given ID doesn't exist
        """
        result = await self.session.execute(
            select(TaskListModel).where(TaskListModel.id == task_list.id)
        )
        task_list_model = result.scalar_one_or_none()

        if task_list_model is None:
            raise TaskListNotFoundError(task_list.id)

        # Update fields
        task_list_model.name = task_list.name
        task_list_model.description = task_list.description
        task_list_model.is_active = task_list.is_active
        task_list_model.updated_at = task_list.updated_at

        await self.session.commit()
        await self.session.refresh(task_list_model)

        return self._to_domain(task_list_model)

    async def delete(self, task_list_id: UUID) -> bool:
        """Delete task list by id.

        Args:
            task_list_id: Unique identifier of the task list to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            select(TaskListModel).where(TaskListModel.id == task_list_id)
        )
        task_list_model = result.scalar_one_or_none()

        if task_list_model is None:
            return False

        await self.session.delete(task_list_model)
        await self.session.commit()
        return True

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
        query = (
            select(TaskListModel)
            .where(
                TaskListModel.owner_id == owner_id,
                TaskListModel.is_active == is_active,
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        task_list_models = result.scalars().all()

        return [
            self._to_domain(task_list_model) for task_list_model in task_list_models
        ]

    async def exists(self, task_list_id: UUID) -> bool:
        """Check if task list exists.

        Args:
            task_list_id: ID of the task list to check

        Returns:
            True if task list exists, False otherwise
        """
        result = await self.session.execute(
            select(TaskListModel.id).where(TaskListModel.id == task_list_id)
        )
        return result.scalar_one_or_none() is not None

    def _to_domain(self, task_list_model: TaskListModel) -> TaskList:
        """Convert SQLAlchemy model to domain entity.

        Args:
            task_list_model: SQLAlchemy task list model

        Returns:
            TaskList domain entity
        """
        return TaskList(
            id=task_list_model.id,
            name=task_list_model.name,
            description=task_list_model.description,
            owner_id=task_list_model.owner_id,
            is_active=task_list_model.is_active,
            created_at=task_list_model.created_at,
            updated_at=task_list_model.updated_at,
        )
