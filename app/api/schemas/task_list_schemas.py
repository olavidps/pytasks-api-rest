"""TaskList API schemas for requests and responses."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common_schemas import PaginatedResponse
from .user_schemas import UserSummary

if TYPE_CHECKING:
    from .task_schemas import TaskResponse


class TaskListBase(BaseModel):
    """Base task list schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Task list name")
    description: Optional[str] = Field(
        None, max_length=500, description="Task list description"
    )


class TaskListCreate(TaskListBase):
    """Schema for creating a new task list."""

    owner_id: Optional[UUID] = Field(default=None)


class TaskListUpdate(BaseModel):
    """Schema for updating a task list."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="New task list name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="New task list description"
    )
    owner_id: Optional[UUID] = Field(default=None)
    is_active: Optional[bool] = Field(default=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskListResponse(TaskListBase):
    """Schema for task list response data."""

    id: UUID = Field(..., description="Task list unique identifier")
    owner_id: Optional[UUID] = Field(None, description="Owner user ID")
    is_active: bool = Field(..., description="Whether task list is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TaskListWithOwner(TaskListResponse):
    """Task list response with owner information."""

    owner: UserSummary = Field(..., description="Task list owner information")


class TaskListWithStats(TaskListResponse):
    """Task list response with task statistics."""

    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    in_progress_tasks: int = Field(..., description="Number of in-progress tasks")
    completion_percentage: float = Field(
        ..., description="Completion percentage (0-100)"
    )


class TaskListSummary(BaseModel):
    """Minimal task list information for references."""

    id: UUID = Field(..., description="Task list unique identifier")
    name: str = Field(..., description="Task list name")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TaskListTasksResponse(TaskListWithStats):
    """Task list response with tasks and statistics."""

    tasks: List["TaskResponse"] = Field(
        ..., description="List of tasks in the task list"
    )


# Type alias for paginated task list response
PaginatedTaskListResponse = PaginatedResponse[TaskListResponse]
