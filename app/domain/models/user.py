"""User domain model."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    """User domain entity."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    def update_profile(
        self,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        email: Optional[EmailStr] = None,
    ) -> "User":
        """Update user profile.

        Args:
            username: New username
            full_name: New full name
            email: New email address

        Returns:
            Updated User instance
        """
        updates = {"updated_at": datetime.now(timezone.utc)}

        if username is not None:
            updates["username"] = username

        if full_name is not None:
            updates["full_name"] = full_name

        if email is not None:
            updates["email"] = email

        return self.model_copy(update=updates)

    def deactivate(self) -> "User":
        """Deactivate user.

        Returns:
            Updated User instance with is_active=False
        """
        return self.model_copy(
            update={
                "is_active": False,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def activate(self) -> "User":
        """Activate user.

        Returns:
            Updated User instance with is_active=True
        """
        return self.model_copy(
            update={
                "is_active": True,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def record_login(self) -> "User":
        """Record user login.

        Returns:
            Updated User instance with current login time
        """
        now = datetime.now(timezone.utc)
        return self.model_copy(
            update={
                "last_login": now,
                "updated_at": now,
            }
        )
