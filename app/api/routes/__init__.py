"""API routes package."""

from .health import router as health_router
from .task_lists import router as task_lists_router
from .tasks import router as tasks_router
from .users import router as users_router

__all__ = [
    "health_router",
    "task_lists_router",
    "tasks_router",
    "users_router",
]
