"""User API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_user_repository
from app.api.schemas import (
    FilterParams,
    PaginatedResponse,
    PaginationParams,
    UserCreate,
    UserResponse,
    UserSummary,
    UserUpdate,
)
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository

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
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Create a new user."""
    try:
        # Check if user already exists by email
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists",
            )

        # Check if username is taken
        if user_data.username:
            existing_username = await user_repo.get_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username {user_data.username} is already taken",
                )

        # Create user domain object
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
        )

        # Create user in repository
        created_user = await user_repo.create(user)
        return UserResponse.model_validate(created_user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e


@router.get(
    "/",
    response_model=PaginatedResponse[UserSummary],
    summary="Get users",
    description="Retrieve a paginated list of users with optional filtering.",
)
async def get_users(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    user_repo: UserRepository = Depends(get_user_repository),
) -> PaginatedResponse[UserSummary]:
    """Get paginated users with optional filtering."""
    try:
        # Build filter criteria
        filter_criteria = {}
        if filters.search:
            filter_criteria["search"] = filters.search
        if filters.is_active is not None:
            filter_criteria["is_active"] = filters.is_active

        # Get paginated results
        users, total = await user_repo.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            filters=filter_criteria,
        )

        # Convert to response models
        user_summaries = [UserSummary.model_validate(user) for user in users]

        return PaginatedResponse.create(
            items=user_summaries,
            page=pagination.page,
            size=pagination.size,
            total=total,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        ) from e


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID.",
)
async def get_user(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Get a specific user by ID."""
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        import traceback

        error_details = f"Failed to retrieve user: {str(e)} - {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details,
        ) from e


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    summary="Get user by email",
    description="Retrieve a specific user by their email address.",
)
async def get_user_by_email(
    email: str,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Get a specific user by email."""
    try:
        user = await user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found",
            )
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        ) from e


@router.get(
    "/username/{username}",
    response_model=UserResponse,
    summary="Get user by username",
    description="Retrieve a specific user by their username.",
)
async def get_user_by_username(
    username: str,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Get a specific user by username."""
    try:
        user = await user_repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username {username} not found",
            )
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        ) from e


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update a specific user with the provided data.",
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Update a specific user."""
    try:
        # Check if user exists
        existing_user = await user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Check if email is being changed and if it's already taken
        if user_data.email and user_data.email != existing_user.email:
            email_user = await user_repo.get_by_email(user_data.email)
            if email_user and email_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email {user_data.email} is already taken",
                )

        # Check if username is being changed and if it's already taken
        if user_data.username and user_data.username != existing_user.username:
            username_user = await user_repo.get_by_username(user_data.username)
            if username_user and username_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username {user_data.username} is already taken",
                )

        # Update user
        updated_user = await user_repo.update(user_id, user_data.to_domain_dict())
        return UserResponse.model_validate(updated_user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        ) from e


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user",
    description="Activate a specific user account.",
)
async def activate_user(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Activate a user account."""
    try:
        # Check if user exists
        existing_user = await user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Activate user
        updated_user = await user_repo.update(user_id, {"is_active": True})
        return UserResponse.model_validate(updated_user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user",
        ) from e


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user",
    description="Deactivate a specific user account.",
)
async def deactivate_user(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Deactivate a user account."""
    try:
        # Check if user exists
        existing_user = await user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Deactivate user
        updated_user = await user_repo.update(user_id, {"is_active": False})
        return UserResponse.model_validate(updated_user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user",
        ) from e


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a specific user by their ID.",
)
async def delete_user(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_user_repository),
) -> None:
    """Delete a specific user."""
    try:
        # Check if user exists
        existing_user = await user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Delete user
        await user_repo.delete(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        ) from e
