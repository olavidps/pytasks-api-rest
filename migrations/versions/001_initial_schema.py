"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-06-22 22:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column(
            "email", sa.String(length=255), nullable=False, unique=True, index=True
        ),
        sa.Column(
            "username", sa.String(length=50), nullable=False, unique=True, index=True
        ),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # Create task_lists table
    op.create_table(
        "task_lists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "owner_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", name="taskstatus"),
            nullable=False,
            default="PENDING",
            index=True,
        ),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="taskpriority"),
            nullable=False,
            default="MEDIUM",
            index=True,
        ),
        sa.Column(
            "task_list_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "assigned_user_id", postgresql.UUID(as_uuid=True), nullable=True, index=True
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["task_list_id"], ["task_lists.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["assigned_user_id"], ["users.id"], ondelete="SET NULL"
        ),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("tasks")
    op.drop_table("task_lists")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS taskpriority")
