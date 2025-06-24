"""Use cases package."""

# Task use cases
# User use cases
from .activate_user import ActivateUserUseCase
from .create_task import CreateTaskUseCase
from .create_user import CreateUserUseCase
from .deactivate_user import DeactivateUserUseCase
from .delete_task import DeleteTaskUseCase
from .delete_user import DeleteUserUseCase
from .get_task import GetTaskUseCase
from .get_tasks import GetTasksUseCase
from .get_user import GetUserUseCase
from .get_users import GetUsersUseCase
from .update_task import UpdateTaskUseCase
from .update_task_assignment import UpdateTaskAssignmentUseCase
from .update_task_priority import UpdateTaskPriorityUseCase
from .update_task_status import UpdateTaskStatusUseCase
from .update_user import UpdateUserUseCase

__all__ = [
    # Task use cases
    "CreateTaskUseCase",
    "DeleteTaskUseCase",
    "GetTaskUseCase",
    "GetTasksUseCase",
    "UpdateTaskUseCase",
    "UpdateTaskAssignmentUseCase",
    "UpdateTaskPriorityUseCase",
    "UpdateTaskStatusUseCase",
    # User use cases
    "ActivateUserUseCase",
    "CreateUserUseCase",
    "DeactivateUserUseCase",
    "DeleteUserUseCase",
    "GetUserUseCase",
    "GetUsersUseCase",
    "UpdateUserUseCase",
]
