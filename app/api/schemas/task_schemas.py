"""Task API schemas for requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.models.task import TaskPriority, TaskStatus

from .common_schemas import PaginatedResponse
from .task_list_schemas import TaskListSummary
from .user_schemas import UserSummary


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    task_list_id: UUID = Field(
        ..., description="ID of the task list this task belongs to"
    )
    assigned_user_id: Optional[UUID] = Field(
        None, description="ID of the assigned user"
    )


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New task title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="New task description"
    )
    priority: Optional[TaskPriority] = Field(None, description="New task priority")
    due_date: Optional[datetime] = Field(None, description="New task due date")
    assigned_user_id: Optional[UUID] = Field(None, description="New assigned user ID")


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""

    status: TaskStatus = Field(..., description="New task status")


class TaskPriorityUpdate(BaseModel):
    """Schema for updating task priority."""

    priority: TaskPriority = Field(..., description="New task priority")


class TaskAssignmentUpdate(BaseModel):
    """Schema for updating task assignment."""

    assigned_user_id: Optional[UUID] = Field(
        None, description="User ID to assign (null to unassign)"
    )


class TaskResponse(TaskBase):
    """Schema for task response data."""

    id: UUID = Field(..., description="Task unique identifier")
    status: TaskStatus = Field(..., description="Current task status")
    task_list_id: UUID = Field(..., description="Task list ID")
    assigned_user_id: Optional[UUID] = Field(None, description="Assigned user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TaskWithRelations(TaskResponse):
    """Task response with related entities."""

    task_list: TaskListSummary = Field(..., description="Task list information")
    assigned_user: Optional[UserSummary] = Field(
        None, description="Assigned user information"
    )


class TaskSummary(BaseModel):
    """Minimal task information for references."""

    id: UUID = Field(..., description="Task unique identifier")
    title: str = Field(..., description="Task title")
    status: TaskStatus = Field(..., description="Task status")
    priority: TaskPriority = Field(..., description="Task priority")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TaskFilterParams(BaseModel):
    """Filtering parameters for task queries."""

    status: Optional[TaskStatus] = Field(None, description="Filter by task status")
    priority: Optional[TaskPriority] = Field(
        None, description="Filter by task priority"
    )
    assigned_to_id: Optional[UUID] = Field(None, description="Filter by assigned user")
    task_list_id: Optional[UUID] = Field(None, description="Filter by task list")
    search: Optional[str] = Field(None, description="Search in title and description")
    due_date_from: Optional[datetime] = Field(
        None, description="Tasks due after this date"
    )
    due_date_to: Optional[datetime] = Field(
        None, description="Tasks due before this date"
    )


# Type alias for paginated task response
PaginatedTaskResponse = PaginatedResponse[TaskResponse]
