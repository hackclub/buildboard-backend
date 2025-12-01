"""add public profile fields to user

Revision ID: 476fc7ec99e1
Revises: 86d6b6532536
Create Date: 2025-12-01 15:10:32.604144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '476fc7ec99e1'
down_revision: Union[str, Sequence[str], None] = 'd9aed0d2f684'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('public_profile_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(length=1000), nullable=True))
    op.create_index(op.f('ix_users_public_profile_url'), 'users', ['public_profile_url'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_public_profile_url'), table_name='users')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'public_profile_url')