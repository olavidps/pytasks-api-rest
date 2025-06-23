"""TaskList domain model."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TaskList(BaseModel):
    """TaskList domain model for organizing tasks."""

    model_config = ConfigDict(frozen=True)  # Make immutable

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    owner_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    def update_details(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> "TaskList":
        """Update task list details.

        Args:
            name: New name for the task list
            description: New description for the task list

        Returns:
            Updated TaskList instance
        """
        updates = {"updated_at": datetime.now(timezone.utc)}

        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description

        return self.model_copy(update=updates)

    def deactivate(self) -> "TaskList":
        """Deactivate task list (soft delete).

        Returns:
            Updated TaskList instance with is_active=False
        """
        return self.model_copy(
            update={
                "is_active": False,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def activate(self) -> "TaskList":
        """Activate task list.

        Returns:
            Updated TaskList instance with is_active=True
        """
        return self.model_copy(
            update={
                "is_active": True,
                "updated_at": datetime.now(timezone.utc),
            }
        )
