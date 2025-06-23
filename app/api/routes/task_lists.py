"""TaskList API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_task_list_repository, get_user_repository
from app.api.schemas import (
    FilterParams,
    PaginatedTaskListResponse,
    PaginationParams,
    TaskListCreate,
    TaskListResponse,
    TaskListUpdate,
    TaskListWithStats,
)
from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.user_repository import UserRepository

router = APIRouter(prefix="/task-lists", tags=["task-lists"])


@router.post(
    "/",
    response_model=TaskListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task list",
    description="Create a new task list with the provided data.",
)
async def create_task_list(
    task_list_data: TaskListCreate,
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TaskListResponse:
    """Create a new task list."""
    # Verify owner exists
    try:
        owner = await user_repo.get_by_id(task_list_data.owner_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {task_list_data.owner_id} not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {task_list_data.owner_id} not found",
        ) from e

    # Create task list
    try:
        task_list = await task_list_repo.create(task_list_data.to_domain())
        return TaskListResponse.from_domain(task_list)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task list",
        ) from e


@router.get(
    "/",
    response_model=PaginatedTaskListResponse,
    summary="Get task lists",
    description="Retrieve a paginated list of task lists with optional filtering.",
)
async def get_task_lists(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    owner_id: Optional[UUID] = Query(None, description="Filter by owner ID"),
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> PaginatedTaskListResponse:
    """Get paginated task lists with optional filtering."""
    try:
        # Build filter criteria
        filter_criteria = {}
        if filters.search:
            filter_criteria["search"] = filters.search
        if filters.is_active is not None:
            filter_criteria["is_active"] = filters.is_active
        if owner_id:
            filter_criteria["owner_id"] = owner_id

        # Get paginated results
        task_lists, total = await task_list_repo.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            filters=filter_criteria,
        )

        # Convert to response models
        task_list_responses = [TaskListResponse.from_domain(tl) for tl in task_lists]

        return PaginatedTaskListResponse.create(
            items=task_list_responses,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task lists",
        ) from e


@router.get(
    "/{task_list_id}",
    response_model=TaskListWithStats,
    summary="Get task list by ID",
    description="Retrieve a specific task list by its ID with statistics.",
)
async def get_task_list(
    task_list_id: UUID,
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> TaskListWithStats:
    """Get a specific task list by ID."""
    try:
        task_list = await task_list_repo.get_by_id(task_list_id)
        if not task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task list with id {task_list_id} not found",
            )
        return TaskListWithStats.from_domain(task_list)
    except TaskListNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task list",
        ) from e


@router.put(
    "/{task_list_id}",
    response_model=TaskListResponse,
    summary="Update task list",
    description="Update a specific task list with the provided data.",
)
async def update_task_list(
    task_list_id: UUID,
    task_list_data: TaskListUpdate,
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> TaskListResponse:
    """Update a specific task list."""
    try:
        # Check if task list exists
        existing_task_list = await task_list_repo.get_by_id(task_list_id)
        if not existing_task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task list with id {task_list_id} not found",
            )

        # Update task list
        updated_task_list = await task_list_repo.update(
            task_list_id, task_list_data.to_domain_dict()
        )
        return TaskListResponse.from_domain(updated_task_list)
    except TaskListNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task list",
        ) from e


@router.delete(
    "/{task_list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task list",
    description="Delete a specific task list by its ID.",
)
async def delete_task_list(
    task_list_id: UUID,
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
) -> None:
    """Delete a specific task list."""
    try:
        # Check if task list exists
        existing_task_list = await task_list_repo.get_by_id(task_list_id)
        if not existing_task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task list with id {task_list_id} not found",
            )

        # Delete task list
        await task_list_repo.delete(task_list_id)
    except TaskListNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task list",
        ) from e
