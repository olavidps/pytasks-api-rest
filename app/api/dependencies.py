"""FastAPI dependency injection functions."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_validation_service import UserValidationService
from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.get_users import GetUsersUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService
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


# User service dependencies
async def get_user_domain_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserDomainService:
    """Get user domain service dependency."""
    return UserDomainService(user_repo)


async def get_user_validation_service(
    user_domain_service: UserDomainService = Depends(get_user_domain_service),
) -> UserValidationService:
    """Get user validation service dependency."""
    return UserValidationService(user_domain_service)


# User use case dependencies
async def get_create_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    validation_service: UserValidationService = Depends(get_user_validation_service),
) -> CreateUserUseCase:
    """Get create user use case dependency."""
    return CreateUserUseCase(user_repo, validation_service)


async def get_update_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    validation_service: UserValidationService = Depends(get_user_validation_service),
) -> UpdateUserUseCase:
    """Get update user use case dependency."""
    return UpdateUserUseCase(user_repo, validation_service)


async def get_get_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetUserUseCase:
    """Get user by ID use case dependency."""
    return GetUserUseCase(user_repo)


async def get_get_users_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetUsersUseCase:
    """Get GetUsersUseCase dependency."""
    return GetUsersUseCase(user_repo)


async def get_activate_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> ActivateUserUseCase:
    """Get activate user use case dependency."""
    return ActivateUserUseCase(user_repo)


async def get_deactivate_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> DeactivateUserUseCase:
    """Get deactivate user use case dependency."""
    return DeactivateUserUseCase(user_repo)


async def get_delete_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> DeleteUserUseCase:
    """Get delete user use case dependency."""
    return DeleteUserUseCase(user_repo)
