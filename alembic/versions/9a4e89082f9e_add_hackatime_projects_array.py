"""add_hackatime_projects_array

Revision ID: 9a4e89082f9e
Revises: d4c07732d7a1
Create Date: 2025-12-09 09:14:45.922768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '9a4e89082f9e'
down_revision: Union[str, Sequence[str], None] = 'd4c07732d7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Upgrade schema."""
    if not column_exists('projects', 'hackatime_projects'):
        op.add_column('projects', sa.Column('hackatime_projects', sa.ARRAY(sa.String()), nullable=True))
    if not column_exists('projects', 'hackatime_hours'):
        op.add_column('projects', sa.Column('hackatime_hours', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    if column_exists('projects', 'hackatime_hours'):
        op.drop_column('projects', 'hackatime_hours')
    if column_exists('projects', 'hackatime_projects'):
        op.drop_column('projects', 'hackatime_projects')
