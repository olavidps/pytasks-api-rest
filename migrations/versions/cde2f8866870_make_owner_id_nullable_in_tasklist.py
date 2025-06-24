"""Make owner_id nullable in TaskList

Revision ID: cde2f8866870
Revises: 001
Create Date: 2025-06-24 00:40:12.410491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cde2f8866870'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('task_lists', 'owner_id', existing_type=sa.UUID(), type_=sa.UUID(), nullable=True, postgresql_using='owner_id::uuid')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('task_lists', 'owner_id', existing_type=sa.UUID(), nullable=False)
