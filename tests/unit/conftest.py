"""Configuration and fixtures for unit tests."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_async_session():
    """Mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_user_repository():
    """Mock user repository for unit tests."""
    repository = AsyncMock()
    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_by_email = AsyncMock()
    repository.get_by_username = AsyncMock()
    repository.get_paginated = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def mock_user_domain_service():
    """Mock user domain service for unit tests."""
    service = AsyncMock()

    return service
