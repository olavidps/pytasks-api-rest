"""Task routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_create_task_use_case,
    get_delete_task_use_case,
    get_get_task_use_case,
    get_get_tasks_use_case,
    get_update_task_assignment_use_case,
    get_update_task_priority_use_case,
    get_update_task_status_use_case,
    get_update_task_use_case,
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
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.delete_task import DeleteTaskUseCase
from app.application.use_cases.get_task import GetTaskUseCase
from app.application.use_cases.get_tasks import GetTasksUseCase
from app.application.use_cases.update_task import UpdateTaskUseCase
from app.application.use_cases.update_task_assignment import UpdateTaskAssignmentUseCase
from app.application.use_cases.update_task_priority import UpdateTaskPriorityUseCase
from app.application.use_cases.update_task_status import UpdateTaskStatusUseCase
from app.domain.exceptions import (
    TaskListNotFoundError,
    TaskNotFoundError,
    UserNotFoundError,
    ValidationError,
)

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
    create_task_use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    """Create a new task."""
    try:
        task = await create_task_use_case.execute(task_data.to_domain())
        return TaskResponse.model_validate(task)
    except TaskListNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
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
    get_tasks_use_case: GetTasksUseCase = Depends(get_get_tasks_use_case),
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
        tasks, total = await get_tasks_use_case.execute(
            pagination=pagination,
            filters=filter_criteria,
        )

        # Convert to response models
        task_responses = [TaskResponse.model_validate(task) for task in tasks]

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
    get_task_use_case: GetTaskUseCase = Depends(get_get_task_use_case),
) -> TaskWithRelations:
    """Get a specific task by ID."""
    try:
        return await get_task_use_case.execute(task_id)
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
    update_task_use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
    get_task_use_case: GetTaskUseCase = Depends(get_get_task_use_case),
) -> TaskResponse:
    """Update a specific task."""
    try:
        existing_task = await get_task_use_case.execute(task_id)

        update_data = task_data.model_dump(exclude_unset=True)

        # Handle specific update methods for immutable Task model
        if (
            "title" in update_data
            or "description" in update_data
            or "due_date" in update_data
        ):
            existing_task = existing_task.update_details(
                title=update_data.get("title"),
                description=update_data.get("description"),
                due_date=update_data.get("due_date"),
            )

        if "priority" in update_data:
            existing_task = existing_task.change_priority(update_data["priority"])

        if "assigned_user_id" in update_data:
            if update_data["assigned_user_id"] is None:
                existing_task = existing_task.unassign()
            else:
                existing_task = existing_task.assign_to_user(
                    update_data["assigned_user_id"]
                )

        updated_task = await update_task_use_case.execute(task_id, existing_task)
        return TaskResponse.model_validate(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    update_task_status_use_case: UpdateTaskStatusUseCase = Depends(
        get_update_task_status_use_case
    ),
) -> TaskResponse:
    """Update task status."""
    try:
        updated_task = await update_task_status_use_case.execute(
            task_id, status_data.status
        )
        return TaskResponse.model_validate(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    update_task_priority_use_case: UpdateTaskPriorityUseCase = Depends(
        get_update_task_priority_use_case
    ),
) -> TaskResponse:
    """Update task priority."""
    try:
        updated_task = await update_task_priority_use_case.execute(
            task_id, priority_data.priority
        )
        return TaskResponse.model_validate(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    update_task_assignment_use_case: UpdateTaskAssignmentUseCase = Depends(
        get_update_task_assignment_use_case
    ),
) -> TaskResponse:
    """Update task assignment."""
    try:
        updated_task = await update_task_assignment_use_case.execute(
            task_id, assignment_data.assigned_to_id
        )
        return TaskResponse.model_validate(updated_task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    delete_task_use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case),
) -> None:
    """Delete a specific task."""
    try:
        await delete_task_use_case.execute(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task",
        ) from e
