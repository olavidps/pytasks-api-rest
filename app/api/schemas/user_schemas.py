"""User API schemas for requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    full_name: str = Field(
        ..., min_length=1, max_length=100, description="User full name"
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass  # Inherits all fields from UserBase


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="New username"
    )
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="New full name"
    )


class UserResponse(UserBase):
    """Schema for user response data."""

    id: UUID = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class UserSummary(BaseModel):
    """Minimal user information for references."""

    id: UUID = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="User full name")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
