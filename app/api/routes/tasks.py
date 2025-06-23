"""Task API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_task_list_repository,
    get_task_repository,
    get_user_repository,
)
from app.api.schemas import (
    PaginatedTaskResponse,
    PaginationParams,
    TaskAssignmentUpdate,
    TaskCreate,
    TaskFilterParams,
    TaskPriorityUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
    TaskWithRelations,
)
from app.domain.exceptions.task import TaskNotFoundError
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with the provided data.",
)
async def create_task(
    task_data: TaskCreate,
    task_repo: TaskRepository = Depends(get_task_repository),
    task_list_repo: TaskListRepository = Depends(get_task_list_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TaskResponse:
    """Create a new task."""
    # Verify task list exists
    try:
        task_list = await task_list_repo.get_by_id(task_data.task_list_id)
        if not task_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task list with id {task_data.task_list_id} not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task list with id {task_data.task_list_id} not found",
        ) from e

    # Verify assigned user exists if provided
    if task_data.assigned_to_id:
        try:
            assigned_user = await user_repo.get_by_id(task_data.assigned_to_id)
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {task_data.assigned_to_id} not found",
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {task_data.assigned_to_id} not found",
            ) from e

    # Create task
    try:
        task = await task_repo.create(task_data.to_domain())
        return TaskResponse.from_domain(task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task",
        ) from e


@router.get(
    "/",
    response_model=PaginatedTaskResponse,
    summary="Get tasks",
    description="Retrieve a paginated list of tasks with optional filtering.",
)
async def get_tasks(
    pagination: PaginationParams = Depends(),
    filters: TaskFilterParams = Depends(),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> PaginatedTaskResponse:
    """Get paginated tasks with optional filtering."""
    try:
        # Build filter criteria
        filter_criteria = {}
        if filters.search:
            filter_criteria["search"] = filters.search
        if filters.status:
            filter_criteria["status"] = filters.status
        if filters.priority:
            filter_criteria["priority"] = filters.priority
        if filters.task_list_id:
            filter_criteria["task_list_id"] = filters.task_list_id
        if filters.assigned_to_id:
            filter_criteria["assigned_to_id"] = filters.assigned_to_id
        if filters.due_date_from:
            filter_criteria["due_date_from"] = filters.due_date_from
        if filters.due_date_to:
            filter_criteria["due_date_to"] = filters.due_date_to

        # Get paginated results
        tasks, total = await task_repo.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            filters=filter_criteria,
        )

        # Convert to response models
        task_responses = [TaskResponse.from_domain(task) for task in tasks]

        return PaginatedTaskResponse.create(
            items=task_responses,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks",
        ) from e


@router.get(
    "/{task_id}",
    response_model=TaskWithRelations,
    summary="Get task by ID",
    description="Retrieve a specific task by its ID with related entities.",
)
async def get_task(
    task_id: UUID,
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskWithRelations:
    """Get a specific task by ID."""
    try:
        task = await task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        return TaskWithRelations.from_domain(task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task",
        ) from e


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update a specific task with the provided data.",
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    task_repo: TaskRepository = Depends(get_task_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TaskResponse:
    """Update a specific task."""
    try:
        # Check if task exists
        existing_task = await task_repo.get_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Verify assigned user exists if provided
        if task_data.assigned_to_id:
            assigned_user = await user_repo.get_by_id(task_data.assigned_to_id)
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {task_data.assigned_to_id} not found",
                )

        # Update task
        updated_task = await task_repo.update(task_id, task_data.to_domain_dict())
        return TaskResponse.from_domain(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task",
        ) from e


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Update task status",
    description="Update only the status of a specific task.",
)
async def update_task_status(
    task_id: UUID,
    status_data: TaskStatusUpdate,
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponse:
    """Update task status."""
    try:
        # Check if task exists
        existing_task = await task_repo.get_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Update task status
        updated_task = await task_repo.update(task_id, {"status": status_data.status})
        return TaskResponse.from_domain(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task status",
        ) from e


@router.patch(
    "/{task_id}/priority",
    response_model=TaskResponse,
    summary="Update task priority",
    description="Update only the priority of a specific task.",
)
async def update_task_priority(
    task_id: UUID,
    priority_data: TaskPriorityUpdate,
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponse:
    """Update task priority."""
    try:
        # Check if task exists
        existing_task = await task_repo.get_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Update task priority
        updated_task = await task_repo.update(
            task_id, {"priority": priority_data.priority}
        )
        return TaskResponse.from_domain(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task priority",
        ) from e


@router.patch(
    "/{task_id}/assignment",
    response_model=TaskResponse,
    summary="Update task assignment",
    description="Update the assignment of a specific task.",
)
async def update_task_assignment(
    task_id: UUID,
    assignment_data: TaskAssignmentUpdate,
    task_repo: TaskRepository = Depends(get_task_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TaskResponse:
    """Update task assignment."""
    try:
        # Check if task exists
        existing_task = await task_repo.get_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Verify assigned user exists if provided
        if assignment_data.assigned_to_id:
            assigned_user = await user_repo.get_by_id(assignment_data.assigned_to_id)
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {assignment_data.assigned_to_id} not found",
                )

        # Update task assignment
        updated_task = await task_repo.update(
            task_id, {"assigned_to_id": assignment_data.assigned_to_id}
        )
        return TaskResponse.from_domain(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task assignment",
        ) from e


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a specific task by its ID.",
)
async def delete_task(
    task_id: UUID,
    task_repo: TaskRepository = Depends(get_task_repository),
) -> None:
    """Delete a specific task."""
    try:
        # Check if task exists
        existing_task = await task_repo.get_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        # Delete task
        await task_repo.delete(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task",
        ) from e
