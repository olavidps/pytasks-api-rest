"""FastAPI dependency injection functions."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.task_list_validation_service import (
    TaskListValidationService,
)
from app.application.services.task_validation_service import TaskValidationService
from app.application.services.user_validation_service import UserValidationService
from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.create_task_list import CreateTaskListUseCase
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.delete_task import DeleteTaskUseCase
from app.application.use_cases.delete_task_list import DeleteTaskListUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.get_task import GetTaskUseCase
from app.application.use_cases.get_task_list import GetTaskListUseCase
from app.application.use_cases.get_tasks import GetTasksUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.get_users import GetUsersUseCase
from app.application.use_cases.update_task import UpdateTaskUseCase
from app.application.use_cases.update_task_assignment import UpdateTaskAssignmentUseCase
from app.application.use_cases.update_task_list import UpdateTaskListUseCase
from app.application.use_cases.update_task_priority import UpdateTaskPriorityUseCase
from app.application.use_cases.update_task_status import UpdateTaskStatusUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.task_domain_service import TaskDomainService
from app.domain.services.task_list_domain_service import TaskListDomainService
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


# Task service dependencies
async def get_task_domain_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> TaskDomainService:
    """Get task domain service dependency."""
    return TaskDomainService(task_repo, user_repo, task_list_repo)


async def get_task_validation_service(
    task_domain_service: TaskDomainService = Depends(get_task_domain_service),
) -> TaskValidationService:
    """Get task validation service dependency."""
    return TaskValidationService(task_domain_service)


# Task use case dependencies
async def get_create_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
    validation_service: TaskValidationService = Depends(get_task_validation_service),
) -> CreateTaskUseCase:
    """Get create task use case dependency."""
    return CreateTaskUseCase(task_repo, validation_service)


async def get_update_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
    validation_service: TaskValidationService = Depends(get_task_validation_service),
) -> UpdateTaskUseCase:
    """Get update task use case dependency."""
    return UpdateTaskUseCase(task_repo, validation_service)


async def get_get_task_use_case(
    task_repository: TaskRepository = Depends(get_task_repository),
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetTaskUseCase:
    """Get task use case dependency."""
    return GetTaskUseCase(task_repository, task_list_repository, user_repository)


async def get_get_tasks_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> GetTasksUseCase:
    """Get GetTasksUseCase dependency."""
    return GetTasksUseCase(task_repo)


# TaskList service dependencies
async def get_task_list_domain_service(
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> TaskListDomainService:
    """Get task list domain service dependency."""
    return TaskListDomainService(task_list_repo)


async def get_task_list_validation_service(
    task_list_domain_service: TaskListDomainService = Depends(
        get_task_list_domain_service
    ),
    user_repository: UserRepository = Depends(get_user_repository),
) -> TaskListValidationService:
    """Get task list validation service dependency."""
    return TaskListValidationService(task_list_domain_service, user_repository)


# TaskList use case dependencies
async def get_create_task_list_use_case(
    task_list_domain_service: TaskListDomainService = Depends(
        get_task_list_domain_service
    ),
    task_list_validation_service: TaskListValidationService = Depends(
        get_task_list_validation_service
    ),
) -> CreateTaskListUseCase:
    """Get create task list use case dependency."""
    return CreateTaskListUseCase(task_list_domain_service, task_list_validation_service)


async def get_task_list_use_case(
    task_list_domain_service: TaskListDomainService = Depends(
        get_task_list_domain_service
    ),
    task_list_validation_service: TaskListValidationService = Depends(
        get_task_list_validation_service
    ),
) -> GetTaskListUseCase:
    """Get get task list use case dependency."""
    return GetTaskListUseCase(task_list_domain_service, task_list_validation_service)


async def get_update_task_list_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_list_validation_service: TaskListValidationService = Depends(
        get_task_list_validation_service
    ),
) -> UpdateTaskListUseCase:
    """Get update task list use case dependency."""
    return UpdateTaskListUseCase(task_list_repository, task_list_validation_service)


async def get_delete_task_list_use_case(
    task_list_domain_service: TaskListDomainService = Depends(
        get_task_list_domain_service
    ),
    task_list_validation_service: TaskListValidationService = Depends(
        get_task_list_validation_service
    ),
) -> DeleteTaskListUseCase:
    """Get delete task list use case dependency."""
    return DeleteTaskListUseCase(task_list_domain_service, task_list_validation_service)


async def get_delete_task_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
    validation_service: TaskValidationService = Depends(get_task_validation_service),
) -> DeleteTaskUseCase:
    """Get delete task use case dependency."""
    return DeleteTaskUseCase(task_repo, validation_service)


async def get_update_task_status_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> UpdateTaskStatusUseCase:
    """Get update task status use case dependency."""
    return UpdateTaskStatusUseCase(task_repo)


async def get_update_task_priority_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> UpdateTaskPriorityUseCase:
    """Get update task priority use case dependency."""
    return UpdateTaskPriorityUseCase(task_repo)


async def get_update_task_assignment_use_case(
    task_repo: TaskRepository = Depends(get_task_repository),
    validation_service: TaskValidationService = Depends(get_task_validation_service),
) -> UpdateTaskAssignmentUseCase:
    """Get update task assignment use case dependency."""
    return UpdateTaskAssignmentUseCase(task_repo, validation_service)
