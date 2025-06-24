"""TaskList SQLAlchemy model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from .task import TaskModel
    from .user import UserModel


class TaskListModel(Base):
    """TaskList SQLAlchemy model."""

    __tablename__ = "task_lists"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="task_lists")
    tasks: Mapped[list["TaskModel"]] = relationship(
        "TaskModel", back_populates="task_list", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return String representation of task list."""
        return f"<TaskListModel(id={self.id}, name={self.name})>"
