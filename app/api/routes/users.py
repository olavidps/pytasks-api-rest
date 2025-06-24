"""User API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_activate_user_use_case,
    get_create_user_use_case,
    get_deactivate_user_use_case,
    get_delete_user_use_case,
    get_get_user_use_case,
    get_get_users_use_case,
    get_update_user_use_case,
)
from app.api.schemas import (
    FilterParams,
    PaginatedResponse,
    PaginationParams,
    UserCreate,
    UserResponse,
    UserSummary,
    UserUpdate,
)
from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.deactivate_user import DeactivateUserUseCase
from app.application.use_cases.delete_user import DeleteUserUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.get_users import GetUsersUseCase
from app.application.use_cases.update_user import UpdateUserUseCase
from app.domain.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided data.",
)
async def create_user(
    user_data: UserCreate,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
    """Create a new user."""
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
    )
    created_user = await use_case.execute(user)
    return UserResponse.model_validate(created_user)


@router.get(
    "/",
    response_model=PaginatedResponse[UserSummary],
    summary="Get users",
    description="Retrieve a paginated list of users with optional filtering.",
)
async def get_users(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    use_case: GetUsersUseCase = Depends(get_get_users_use_case),
) -> PaginatedResponse[UserSummary]:
    """Get paginated users with optional filtering."""
    # Get paginated results using use case
    users, total = await use_case.execute(pagination, filters)

    # Convert to response models
    user_summaries = [UserSummary.model_validate(user) for user in users]

    return PaginatedResponse.create(
        items=user_summaries,
        page=pagination.page,
        size=pagination.size,
        total=total,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID.",
)
async def get_user(
    user_id: UUID,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
) -> UserResponse:
    """Get a specific user by ID."""
    user = await use_case.execute(user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update a specific user with the provided data.",
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
) -> UserResponse:
    """Update a user."""
    updated_user = await use_case.execute(user_id, user_data)
    return UserResponse.model_validate(updated_user)


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user",
    description="Activate a specific user account.",
)
async def activate_user(
    user_id: UUID,
    use_case: ActivateUserUseCase = Depends(get_activate_user_use_case),
) -> UserResponse:
    """Activate a user account."""
    activated_user = await use_case.execute(user_id)
    return UserResponse.model_validate(activated_user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user",
    description="Deactivate a specific user account.",
)
async def deactivate_user(
    user_id: UUID,
    use_case: DeactivateUserUseCase = Depends(get_deactivate_user_use_case),
) -> UserResponse:
    """Deactivate a user account."""
    deactivated_user = await use_case.execute(user_id)
    return UserResponse.model_validate(deactivated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a specific user by their ID.",
)
async def delete_user(
    user_id: UUID,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> None:
    """Delete a user."""
    await use_case.execute(user_id)
