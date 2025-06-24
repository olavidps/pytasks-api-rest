"""Get users use case module."""

from typing import Tuple

from app.api.schemas import FilterParams, PaginationParams
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class GetUsersUseCase:
    """Use case for retrieving paginated users with optional filtering."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(
        self,
        pagination: PaginationParams,
        filters: FilterParams,
    ) -> Tuple[list[User], int]:
        """Execute the get users use case.

        Args:
            pagination: Pagination parameters
            filters: Filter parameters

        Returns:
            Tuple containing list of users and total count
        """
        # Build filter criteria
        filter_criteria = {}
        if filters.search:
            filter_criteria["search"] = filters.search
        if filters.is_active is not None:
            filter_criteria["is_active"] = filters.is_active

        # Get paginated results
        users, total = await self._user_repository.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            filters=filter_criteria,
        )

        return users, total
