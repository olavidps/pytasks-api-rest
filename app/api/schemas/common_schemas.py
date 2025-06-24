"""Common schemas for API requests and responses."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T] = Field(..., description="List of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(
        cls, items: List[T], page: int, size: int, total: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response with items and metadata."""
        pages = (total + size - 1) // size  # Ceiling division
        return cls(items=items, page=page, size=size, total=total, pages=pages)


class FilterParams(BaseModel):
    """Common filtering parameters."""

    search: Optional[str] = Field(None, description="Search term for title/description")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
