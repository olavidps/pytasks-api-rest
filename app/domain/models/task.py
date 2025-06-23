"""Task domain model."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enumerations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enumerations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Task domain entity."""

    model_config = ConfigDict(frozen=True, use_enum_values=True)  # Make immutable

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    task_list_id: UUID
    assigned_user_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def mark_as_in_progress(self) -> "Task":
        """Mark task as in progress.

        Returns:
            Updated Task instance with in_progress status
        """
        return self.model_copy(
            update={
                "status": TaskStatus.IN_PROGRESS,
                "updated_at": datetime.now(timezone.utc),
                "completed_at": None,
            }
        )

    def mark_as_completed(self) -> "Task":
        """Mark task as completed.

        Returns:
            Updated Task instance with completed status and timestamp
        """
        return self.model_copy(
            update={
                "status": TaskStatus.COMPLETED,
                "updated_at": datetime.now(timezone.utc),
                "completed_at": datetime.now(timezone.utc),
            }
        )

    def mark_as_pending(self) -> "Task":
        """Mark task as pending.

        Returns:
            Updated Task instance with pending status
        """
        return self.model_copy(
            update={
                "status": TaskStatus.PENDING,
                "updated_at": datetime.now(timezone.utc),
                "completed_at": None,
            }
        )

    def change_priority(self, priority: TaskPriority) -> "Task":
        """Change task priority.

        Args:
            priority: New priority level for the task

        Returns:
            Updated Task instance with new priority
        """
        return self.model_copy(
            update={
                "priority": priority,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def assign_to_user(self, user_id: UUID) -> "Task":
        """Assign task to a user.

        Args:
            user_id: ID of user to assign the task to

        Returns:
            Updated Task instance with new assignee
        """
        return self.model_copy(
            update={
                "assigned_user_id": user_id,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> "Task":
        """Update task details.

        Args:
            title: New title for the task
            description: New description for the task
            due_date: New due date for the task

        Returns:
            Updated Task instance
        """
        updates = {"updated_at": datetime.now(timezone.utc)}

        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if due_date is not None:
            updates["due_date"] = due_date

        return self.model_copy(update=updates)

    @property
    def is_completed(self) -> bool:
        """Check if task is completed.

        Returns:
            True if task status is completed, False otherwise
        """
        return self.status == TaskStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue.

        Returns:
            True if task has due date in the past and is not completed
        """
        if self.due_date is None or self.is_completed:
            return False
        return datetime.now(timezone.utc) > self.due_date
