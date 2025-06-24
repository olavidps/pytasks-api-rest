"""Extended tests for User domain model."""

from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.domain.models.user import User


class TestUserModelExtended:
    """Extended test cases for User model."""

    def test_user_update_profile_all_fields(self):
        """Test updating all profile fields."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        updated_user = user.update_profile(
            username="newuser", full_name="New User", email="new@example.com"
        )

        assert updated_user.username == "newuser"
        assert updated_user.full_name == "New User"
        assert updated_user.email == "new@example.com"
        assert updated_user.updated_at > user.updated_at
        assert updated_user.id == user.id

    def test_user_update_profile_partial(self):
        """Test updating only some profile fields."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        updated_user = user.update_profile(username="newuser")

        assert updated_user.username == "newuser"
        assert updated_user.full_name == "Test User"  # unchanged
        assert updated_user.email == "test@example.com"  # unchanged
        assert updated_user.updated_at > user.updated_at

    def test_user_update_profile_no_changes(self):
        """Test update profile with no changes."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        updated_user = user.update_profile()

        assert updated_user.username == user.username
        assert updated_user.full_name == user.full_name
        assert updated_user.email == user.email
        assert updated_user.updated_at > user.updated_at

    def test_user_deactivate(self):
        """Test user deactivation."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )

        deactivated_user = user.deactivate()

        assert deactivated_user.is_active is False
        assert deactivated_user.updated_at > user.updated_at
        assert deactivated_user.id == user.id
        assert deactivated_user.email == user.email

    def test_user_activate(self):
        """Test user activation."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=False,
        )

        activated_user = user.activate()

        assert activated_user.is_active is True
        assert activated_user.updated_at > user.updated_at
        assert activated_user.id == user.id
        assert activated_user.email == user.email

    def test_user_record_login(self):
        """Test recording user login."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            last_login=None,
        )

        logged_in_user = user.record_login()

        assert logged_in_user.last_login is not None
        assert logged_in_user.last_login == logged_in_user.updated_at
        assert logged_in_user.updated_at > user.updated_at
        assert logged_in_user.id == user.id

    def test_user_record_login_updates_existing(self):
        """Test recording login updates existing login time."""
        old_login = datetime.now(timezone.utc)
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            last_login=old_login,
        )

        logged_in_user = user.record_login()

        assert logged_in_user.last_login > old_login
        assert logged_in_user.last_login == logged_in_user.updated_at

    def test_user_validation_errors(self):
        """Test user validation errors."""
        # Test invalid email
        with pytest.raises(ValidationError):
            User(email="invalid-email", username="testuser", full_name="Test User")

        # Test username too short
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                username="ab",  # less than 3 characters
                full_name="Test User",
            )

        # Test username too long
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                username="a" * 51,  # more than 50 characters
                full_name="Test User",
            )

        # Test full_name empty
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                username="testuser",
                full_name="",  # empty string
            )

        # Test full_name too long
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                username="testuser",
                full_name="a" * 101,  # more than 100 characters
            )

    def test_user_immutability(self):
        """Test that User model is immutable."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        # Should not be able to modify attributes directly
        with pytest.raises(ValidationError):
            user.email = "new@example.com"

        with pytest.raises(ValidationError):
            user.username = "newuser"

    def test_user_id_generation(self):
        """Test that user ID is automatically generated."""
        user1 = User(
            email="test1@example.com", username="testuser1", full_name="Test User 1"
        )

        user2 = User(
            email="test2@example.com", username="testuser2", full_name="Test User 2"
        )

        assert isinstance(user1.id, UUID)
        assert isinstance(user2.id, UUID)
        assert user1.id != user2.id

    def test_user_default_values(self):
        """Test user default values."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        assert user.is_active is True
        assert user.last_login is None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at.tzinfo == timezone.utc
        assert user.updated_at.tzinfo == timezone.utc
