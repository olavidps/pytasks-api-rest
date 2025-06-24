"""Task validation service for application layer validation logic."""

from typing import Optional
from uuid import UUID

from app.domain.exceptions.task import TaskNotFoundError
from app.domain.exceptions.user import UserNotFoundError
from app.domain.models.task import Task
from app.domain.services.task_domain_service import TaskDomainService


class TaskValidationService:
    """Service to handle task validation logic at the application layer."""

    def __init__(self, task_domain_service: TaskDomainService):
        self.task_domain_service = task_domain_service

    async def validate_task_creation(
        self, task_data: Task, creator_user_id: Optional[UUID] = None
    ) -> None:
        """Validate that a task can be created with the provided data.

        Args:
            task_data: Task data to validate
            creator_user_id: ID of the user creating the task

        Raises:
            TaskListNotFoundError: If task list doesn't exist or user doesn't have access
            UserNotFoundError: If assigned user doesn't exist or is inactive
            ValueError: If task data is invalid
        """
        # Validate task list ownership/access
        # has_access = await self.task_domain_service.validate_task_list_ownership(
        #     task_data.task_list_id, creator_user_id
        # )
        # if not has_access:
        #     raise TaskListNotFoundError(
        #         f"Task list with id {task_data.task_list_id} not found or access denied"
        #     )

        # Validate task assignment if provided
        if task_data.assigned_user_id:
            await self._validate_task_assignment(
                task_data.id, task_data.assigned_user_id
            )

        # Validate due date consistency
        if not await self.task_domain_service.validate_due_date_consistency(task_data):
            raise ValueError("Due date is inconsistent with task status")

    async def validate_task_update(
        self, task_id: UUID, task_data: Task, updater_user_id: Optional[UUID] = None
    ) -> None:
        """Validate that a task can be updated with the provided data.

        Args:
            task_id: ID of the task being updated
            task_data: Updated task data to validate
            updater_user_id: ID of the user updating the task

        Raises:
            TaskNotFoundError: If task doesn't exist
            UserNotFoundError: If assigned user doesn't exist or is inactive
            ValueError: If task data is invalid
        """
        # Validate task assignment if provided
        if task_data.assigned_user_id:
            await self._validate_task_assignment(task_id, task_data.assigned_user_id)

        # Validate due date consistency
        if not await self.task_domain_service.validate_due_date_consistency(task_data):
            raise ValueError("Due date is inconsistent with task status")

    async def validate_task_assignment_update(
        self, task_id: UUID, assigned_user_id: Optional[UUID]
    ) -> None:
        """Validate that a task assignment can be updated.

        Args:
            task_id: ID of the task
            assigned_user_id: ID of the user to assign the task to (None to unassign)

        Raises:
            UserNotFoundError: If assigned user doesn't exist or is inactive
        """
        await self._validate_task_assignment(task_id, assigned_user_id)

    async def validate_task_deletion(self, task_id: UUID) -> None:
        """Validate that a task can be deleted.

        Args:
            task_id: ID of the task to delete

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValueError: If task cannot be deleted due to business rules
        """
        can_delete, reason = await self.task_domain_service.can_task_be_deleted(task_id)
        if not can_delete:
            if "not found" in reason.lower():
                raise TaskNotFoundError(task_id)
            else:
                raise ValueError(reason)

    async def _validate_task_assignment(
        self, task_id: UUID, assigned_user_id: Optional[UUID]
    ) -> None:
        """Validate task assignment.

        Args:
            task_id: ID of the task
            assigned_user_id: ID of the user to assign the task to

        Raises:
            UserNotFoundError: If assigned user doesn't exist or is inactive
        """
        is_valid = await self.task_domain_service.validate_task_assignment(
            task_id, assigned_user_id
        )
        if not is_valid:
            if assigned_user_id:
                raise UserNotFoundError(
                    f"User with id {assigned_user_id} not found or is inactive"
                )
