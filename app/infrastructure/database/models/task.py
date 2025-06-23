"""Task SQLAlchemy model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.task import TaskPriority, TaskStatus
from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from .task_list import TaskListModel
    from .user import UserModel


class TaskModel(Base):
    """Task SQLAlchemy model."""

    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, index=True
    )
    task_list_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("task_lists.id"), index=True
    )
    assigned_user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    task_list: Mapped["TaskListModel"] = relationship(
        "TaskListModel", back_populates="tasks"
    )
    assigned_user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel", foreign_keys=[assigned_user_id], back_populates="assigned_tasks"
    )

    def __repr__(self) -> str:
        """Return String representation of task."""
        return f"<TaskModel(id={self.id}, title={self.title}, status={self.status})>"
