"""User SQLAlchemy model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from .task import TaskModel
    from .task_list import TaskListModel


class UserModel(Base):
    """User SQLAlchemy model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    task_lists: Mapped[list["TaskListModel"]] = relationship(
        "TaskListModel", back_populates="owner", cascade="all, delete-orphan"
    )
    assigned_tasks: Mapped[list["TaskModel"]] = relationship(
        "TaskModel", back_populates="assigned_user"
    )

    def __repr__(self) -> str:
        """Return String representation of user."""
        return f"<UserModel(id={self.id}, username={self.username})>"
