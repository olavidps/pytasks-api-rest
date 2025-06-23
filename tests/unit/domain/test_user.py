"""Unit tests for User domain model."""

from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.models.user import User


class TestUser:
    """Unit tests for User domain entity."""

    def test_create_user_success(self):
        """Test successful user creation with valid data."""
        user_id = uuid4()
        email = "test@example.com"
        username = "testuser"
        full_name = "Test User"

        user = User(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert user.id == user_id
        assert user.email == email
        assert user.username == username
        assert user.full_name == full_name
        assert user.is_active is True

    def test_create_user_invalid_email(self):
        """Test user creation with invalid email format."""
        with pytest.raises(ValueError):
            User(
                id=uuid4(),
                email="invalid-email",
                username="testuser",
                full_name="Test User",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_user_deactivate(self):
        """Test user deactivation method."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        deactivated_user = user.deactivate()

        assert deactivated_user.is_active is False
        assert deactivated_user.id == user.id
        assert deactivated_user.email == user.email

    def test_user_activate(self):
        """Test user activation method."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        activated_user = user.activate()

        assert activated_user.is_active is True
        assert activated_user.id == user.id
        assert activated_user.email == user.email

    def test_user_record_login(self):
        """Test recording user login."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        updated_user = user.record_login()

        assert updated_user.last_login is not None
        assert updated_user.id == user.id
