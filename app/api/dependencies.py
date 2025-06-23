"""FastAPI dependency injection functions."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.repositories.task_list_repository_impl import (
    TaskListRepositoryImpl,
)
from app.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session
    """
    async for session in get_db_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Get user repository dependency.

    Args:
        session: Database session

    Returns:
        UserRepository: User repository instance
    """
    return UserRepositoryImpl(session)


async def get_task_list_repository(
    session: AsyncSession = Depends(get_db),
) -> TaskListRepository:
    """Get task list repository dependency.

    Args:
        session: Database session

    Returns:
        TaskListRepository: Task list repository instance
    """
    return TaskListRepositoryImpl(session)


async def get_task_repository(
    session: AsyncSession = Depends(get_db),
) -> TaskRepository:
    """Get task repository dependency.

    Args:
        session: Database session

    Returns:
        TaskRepository: Task repository instance
    """
    return TaskRepositoryImpl(session)
