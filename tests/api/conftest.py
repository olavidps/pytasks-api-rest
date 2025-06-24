"""Fixtures for API tests using mocks.

This module provides fixtures for testing API endpoints using mocks
instead of real database connections, improving test speed and reliability."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.api.dependencies import (
    get_create_user_use_case,
    get_get_user_use_case,
    get_get_users_use_case,
    get_update_user_use_case,
    get_delete_user_use_case,
    get_activate_user_use_case,
    get_deactivate_user_use_case,
)


@pytest.fixture
def mock_create_user_use_case():
    """Mock the CreateUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_create_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_create_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_create_user_use_case]


@pytest.fixture
def mock_get_user_use_case():
    """Mock the GetUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_get_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_get_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_get_user_use_case]


@pytest.fixture
def mock_get_users_use_case():
    """Mock the GetUsersUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_get_users_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_get_users_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_get_users_use_case]


@pytest.fixture
def mock_update_user_use_case():
    """Mock the UpdateUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_update_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_update_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_update_user_use_case]


@pytest.fixture
def mock_delete_user_use_case():
    """Mock the DeleteUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_delete_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_delete_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_delete_user_use_case]


@pytest.fixture
def mock_activate_user_use_case():
    """Mock the ActivateUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_activate_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_activate_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_activate_user_use_case]


@pytest.fixture
def mock_deactivate_user_use_case():
    """Mock the DeactivateUserUseCase dependency."""
    mock_use_case = AsyncMock()
    app.dependency_overrides[get_deactivate_user_use_case] = lambda: mock_use_case
    yield mock_use_case
    # Cleanup
    if get_deactivate_user_use_case in app.dependency_overrides:
        del app.dependency_overrides[get_deactivate_user_use_case]


@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sync_client():
    """Create a synchronous HTTP client for testing."""
    with TestClient(app) as client:
        yield client