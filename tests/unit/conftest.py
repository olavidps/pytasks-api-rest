"""Configuration for unit tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for unit tests without database dependencies."""
    return TestClient(app)
