"""Domain exceptions package."""

from . import base, task, task_list, user
from .base import AlreadyExistsError, DomainException, NotFoundError, ValidationError
from .task import TaskNotFoundError
from .task_list import TaskListAlreadyExistsError, TaskListNotFoundError
from .user import UnauthorizedOperationError, UserAlreadyExistsError, UserNotFoundError

__all__ = [
    "DomainException",
    "ValidationError",
    "NotFoundError",
    "AlreadyExistsError",
    "TaskNotFoundError",
    "TaskListNotFoundError",
    "UserNotFoundError",
    "TaskListAlreadyExistsError",
    "UserAlreadyExistsError",
    "UnauthorizedOperationError",
    "base",
    "task",
    "task_list",
    "user",
]
