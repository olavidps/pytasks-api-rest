"""Task repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.models.task import TaskModel


class TaskRepositoryImpl(TaskRepository):
    """Task repository implementation using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: Database session
        """
        self.session = session

    async def create(self, task: Task) -> Task:
        """Create a new task.

        Args:
            task: Task entity to create

        Returns:
            Created task with generated ID
        """
        # Create new task model
        task_model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            task_list_id=task.task_list_id,
            assigned_user_id=task.assigned_user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            due_date=task.due_date,
            completed_at=task.completed_at,
        )

        self.session.add(task_model)
        await self.session.commit()
        await self.session.refresh(task_model)

        return self._to_domain(task_model)

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by id.

        Args:
            task_id: Unique identifier of the task

        Returns:
            Task if found, None otherwise
        """
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model = result.scalar_one_or_none()

        if task_model is None:
            return None

        return self._to_domain(task_model)

    async def update(self, task: Task) -> Task:
        """Update task.

        Args:
            task: Task entity with updated values

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model = result.scalar_one_or_none()

        if task_model is None:
            raise TaskNotFoundError(task.id)

        # Update fields
        task_model.title = task.title
        task_model.description = task.description
        task_model.status = task.status
        task_model.priority = task.priority
        task_model.assigned_user_id = task.assigned_user_id
        task_model.updated_at = task.updated_at
        task_model.due_date = task.due_date
        task_model.completed_at = task.completed_at

        await self.session.commit()
        await self.session.refresh(task_model)

        return self._to_domain(task_model)

    async def delete(self, task_id: UUID) -> bool:
        """Delete task by id.

        Args:
            task_id: Unique identifier of the task to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model = result.scalar_one_or_none()

        if task_model is None:
            return False

        await self.session.delete(task_model)
        await self.session.commit()
        return True

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
        query = select(TaskModel).where(TaskModel.task_list_id == task_list_id)

        if status is not None:
            query = query.where(TaskModel.status == status)

        if priority is not None:
            query = query.where(TaskModel.priority == priority)

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        task_models = result.scalars().all()

        return [self._to_domain(task_model) for task_model in task_models]

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
        query = select(TaskModel).where(TaskModel.assigned_user_id == user_id)

        if status is not None:
            query = query.where(TaskModel.status == status)

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        task_models = result.scalars().all()

        return [self._to_domain(task_model) for task_model in task_models]

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
        query = select(func.count(TaskModel.id)).where(
            TaskModel.task_list_id == task_list_id
        )

        if status is not None:
            query = query.where(TaskModel.status == status)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, task_id: UUID) -> bool:
        """Check if task exists.

        Args:
            task_id: ID of the task to check

        Returns:
            True if task exists, False otherwise
        """
        result = await self.session.execute(
            select(TaskModel.id).where(TaskModel.id == task_id)
        )
        return result.scalar_one_or_none() is not None

    def _to_domain(self, task_model: TaskModel) -> Task:
        """Convert SQLAlchemy model to domain entity.

        Args:
            task_model: SQLAlchemy task model

        Returns:
            Task domain entity
        """
        return Task(
            id=task_model.id,
            title=task_model.title,
            description=task_model.description,
            status=task_model.status,
            priority=task_model.priority,
            task_list_id=task_model.task_list_id,
            assigned_user_id=task_model.assigned_user_id,
            created_at=task_model.created_at,
            updated_at=task_model.updated_at,
            due_date=task_model.due_date,
            completed_at=task_model.completed_at,
        )
