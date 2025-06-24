"""TaskList repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.models.task import Task
from app.domain.models.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository
from app.infrastructure.database.models.task import TaskModel
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

    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Get task list by id.

        Args:
            task_list_id: Unique identifier of the task list

        Returns:
            TaskList if found, None otherwise
        """
        result = await self.session.execute(
            select(TaskListModel)
            .where(TaskListModel.id == task_list_id)
            .options(joinedload(TaskListModel.tasks))
        )
        task_list_model = result.unique().scalar_one_or_none()

        if task_list_model is None:
            return None

        if task_list_model is not None:
            await self.session.refresh(task_list_model)

        return self._to_domain(task_list_model)

    def _to_domain(self, task_list_model: TaskListModel) -> TaskList:
        """Convert SQLAlchemy TaskListModel to domain TaskList.

        Args:
            task_list_model: SQLAlchemy TaskListModel object

        Returns:
            TaskList domain object
        """
        tasks = []
        if task_list_model.tasks:
            task_models = task_list_model.tasks
            if task_models:
                for task_model in task_models:
                    tasks.append(
                        Task(
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
                    )

        return TaskList(
            id=task_list_model.id,
            name=task_list_model.name,
            description=task_list_model.description,
            owner_id=task_list_model.owner_id,
            is_active=task_list_model.is_active,
            created_at=task_list_model.created_at,
            updated_at=task_list_model.updated_at,
            tasks=tasks,
        )

    async def update(self, task_list_id: UUID, task_list: TaskList) -> TaskList:
        """Update task list.

        Args:
            task_list: TaskList entity with updated values

        Returns:
            Updated task list

        Raises:
            TaskListNotFoundError: If task list with given ID doesn't exist
        """
        result = await self.session.execute(
            select(TaskListModel)
            .where(TaskListModel.id == task_list_id)
            .options(joinedload(TaskListModel.tasks))
        )
        task_list_model = result.unique().scalar_one_or_none()

        if task_list_model is None:
            raise TaskListNotFoundError(task_list_id)

        if task_list_model is not None:
            await self.session.refresh(task_list_model)

        # Update fields from the provided TaskList domain object
        task_list_model.name = task_list.name
        task_list_model.description = task_list.description
        task_list_model.is_active = task_list.is_active
        task_list_model.updated_at = task_list.updated_at
        task_list_model.owner_id = task_list.owner_id

        await self.session.commit()
        await self.session.refresh(task_list_model)

        return self._to_domain(task_list_model)

    async def delete(self, task_list_id: UUID) -> bool:
        """Delete task list by id and all associated tasks.

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

        # Delete all tasks associated with this task list
        await self.session.execute(
            delete(TaskModel).where(TaskModel.task_list_id == task_list_id)
        )

        # Delete the task list
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

    async def get_paginated(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> tuple[List[TaskList], int]:
        """Get paginated task lists with optional filters.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply

        Returns:
            Tuple containing list of task lists and total count
        """
        # Build base query
        query = select(TaskListModel)
        count_query = select(func.count(TaskListModel.id))

        # Apply filters if provided
        if filters:
            # Filter by owner_id
            if "owner_id" in filters and filters["owner_id"]:
                query = query.where(TaskListModel.owner_id == filters["owner_id"])
                count_query = count_query.where(
                    TaskListModel.owner_id == filters["owner_id"]
                )

            # Filter by is_active
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.where(TaskListModel.is_active == filters["is_active"])
                count_query = count_query.where(
                    TaskListModel.is_active == filters["is_active"]
                )

            # Filter by search term (name or description)
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                search_condition = TaskListModel.name.ilike(
                    search_term
                ) | TaskListModel.description.ilike(search_term)
                query = query.where(search_condition)
                count_query = count_query.where(search_condition)

        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and get results
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        task_list_models = result.scalars().all()

        # Convert to domain entities
        task_lists = [
            self._to_domain(task_list_model) for task_list_model in task_list_models
        ]

        return task_lists, total
