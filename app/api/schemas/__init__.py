"""API Schemas package initialization."""

# Common schemas
from .common_schemas import FilterParams, PaginatedResponse, PaginationParams

# Task list schemas
from .task_list_schemas import (
    PaginatedTaskListResponse,
    TaskListCreate,
    TaskListResponse,
    TaskListSummary,
    TaskListUpdate,
    TaskListWithOwner,
    TaskListWithStats,
)

# Task schemas
from .task_schemas import (
    PaginatedTaskResponse,
    TaskAssignmentUpdate,
    TaskCreate,
    TaskFilterParams,
    TaskPriorityUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskSummary,
    TaskUpdate,
    TaskWithRelations,
)

# User schemas
from .user_schemas import UserCreate, UserResponse, UserSummary, UserUpdate

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "FilterParams",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserSummary",
    # Task List
    "TaskListCreate",
    "TaskListUpdate",
    "TaskListResponse",
    "TaskListSummary",
    "TaskListWithOwner",
    "TaskListWithStats",
    "PaginatedTaskListResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskSummary",
    "TaskWithRelations",
    "TaskStatusUpdate",
    "TaskPriorityUpdate",
    "TaskAssignmentUpdate",
    "TaskFilterParams",
    "PaginatedTaskResponse",
]
