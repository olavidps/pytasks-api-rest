"""Task list validation service module."""

from uuid import UUID

from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.exceptions.user import UserNotFoundError
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.task_list_domain_service import TaskListDomainService


class TaskListValidationService:
    """Service for validating task list related operations."""

    def __init__(
        self,
        task_list_domain_service: TaskListDomainService,
        user_repository: UserRepository,
    ):
        self._task_list_domain_service = task_list_domain_service
        self._user_repository = user_repository

    async def validate_task_list_exists(self, task_list_id: UUID):
        """Validate if a task list exists."""
        if not await self._task_list_domain_service.task_list_exists(task_list_id):
            raise TaskListNotFoundError(task_list_id)

    async def validate_owner_exists(self, owner_id: UUID):
        """Validate if the owner user exists."""
        if not await self._user_repository.get_by_id(owner_id):
            raise UserNotFoundError(owner_id)
