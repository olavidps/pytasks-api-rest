"""TaskList API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_create_task_list_use_case,
    get_delete_task_list_use_case,
    get_get_tasks_use_case,
    get_task_list_use_case,
    get_update_task_list_use_case,
)
from app.api.schemas import (
    FilterParams,
    PaginatedTaskListResponse,
    PaginationParams,
    TaskFilterParams,
    TaskListCreate,
    TaskListResponse,
    TaskListTasksResponse,
    TaskListUpdate,
    TaskListWithStats,
    TaskResponse,
)
from app.application.use_cases.create_task_list import CreateTaskListUseCase
from app.application.use_cases.delete_task_list import DeleteTaskListUseCase
from app.application.use_cases.get_task_list import GetTaskListUseCase
from app.application.use_cases.get_tasks import GetTasksUseCase
from app.application.use_cases.update_task_list import UpdateTaskListUseCase
from app.domain.exceptions.task_list import TaskListNotFoundError
from app.domain.exceptions.user import UserNotFoundError

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
    create_task_list_use_case: CreateTaskListUseCase = Depends(
        get_create_task_list_use_case
    ),
) -> TaskListResponse:
    """Create a new task list."""
    try:
        task_list = await create_task_list_use_case.execute(task_list_data)
        return TaskListResponse.model_validate(task_list)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
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
    get_task_list_use_case: GetTaskListUseCase = Depends(get_task_list_use_case),
) -> PaginatedTaskListResponse:
    """Get paginated task lists with optional filtering."""
    try:
        return await get_task_list_use_case.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            filters={
                "search": filters.search,
                "is_active": filters.is_active,
                "owner_id": owner_id,
            },
            page=pagination.page,
            size=pagination.size,
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
    get_task_list_use_case: GetTaskListUseCase = Depends(get_task_list_use_case),
) -> TaskListWithStats:
    """Get a specific task list by ID."""
    try:
        return await get_task_list_use_case.get_by_id(task_list_id)
    except TaskListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task list",
        ) from e


@router.get(
    "/{task_list_id}/tasks",
    response_model=TaskListTasksResponse,
    summary="Get tasks in task list",
    description="Retrieve all tasks within a specific task list with optional filtering and completion percentage.",
)
async def get_task_list_tasks(
    task_list_id: UUID,
    pagination: PaginationParams = Depends(),
    task_filters: TaskFilterParams = Depends(),
    get_task_list_use_case: GetTaskListUseCase = Depends(get_task_list_use_case),
    get_tasks_use_case: GetTasksUseCase = Depends(get_get_tasks_use_case),
) -> TaskListTasksResponse:
    """Get tasks within a specific task list with filtering and statistics."""
    try:
        # First verify the task list exists and get its statistics
        task_list_stats = await get_task_list_use_case.get_by_id(task_list_id)

        # Prepare filters for tasks, including the task_list_id
        filters = {
            "task_list_id": task_list_id,
            "status": task_filters.status,
            "priority": task_filters.priority,
            "assigned_to_id": task_filters.assigned_to_id,
            "search": task_filters.search,
            "due_date_from": task_filters.due_date_from,
            "due_date_to": task_filters.due_date_to,
        }

        # Get filtered tasks
        tasks, _ = await get_tasks_use_case.execute(pagination, filters)

        # Convert tasks to response format
        task_responses = [TaskResponse.model_validate(task) for task in tasks]

        # Create the response combining task list stats with tasks
        return TaskListTasksResponse(
            id=task_list_stats.id,
            name=task_list_stats.name,
            description=task_list_stats.description,
            owner_id=task_list_stats.owner_id,
            is_active=task_list_stats.is_active,
            created_at=task_list_stats.created_at,
            updated_at=task_list_stats.updated_at,
            total_tasks=task_list_stats.total_tasks,
            completed_tasks=task_list_stats.completed_tasks,
            pending_tasks=task_list_stats.pending_tasks,
            in_progress_tasks=task_list_stats.in_progress_tasks,
            completion_percentage=task_list_stats.completion_percentage,
            tasks=task_responses,
        )
    except TaskListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task list tasks",
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
    update_task_list_use_case: UpdateTaskListUseCase = Depends(
        get_update_task_list_use_case
    ),
    get_task_list_use_case: GetTaskListUseCase = Depends(get_task_list_use_case),
) -> TaskListResponse:
    """Update a specific task list."""
    try:
        updated_task_list = await update_task_list_use_case.execute(
            task_list_id, task_list_data
        )

        return TaskListResponse.model_validate(updated_task_list)
    except TaskListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
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
    delete_task_list_use_case: DeleteTaskListUseCase = Depends(
        get_delete_task_list_use_case
    ),
) -> None:
    """Delete a specific task list."""
    try:
        await delete_task_list_use_case.execute(task_list_id)
    except TaskListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
