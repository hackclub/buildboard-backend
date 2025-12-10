"""auto_migration

Revision ID: afe9408d66b0
Revises: 67539c76e503
Create Date: 2025-12-08 10:04:00.915964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'afe9408d66b0'
down_revision: Union[str, Sequence[str], None] = '67539c76e503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Upgrade schema."""
    if not column_exists('users', 'verification_status'):
        op.add_column('users', sa.Column('verification_status', sa.String(length=32), nullable=True))
    if not column_exists('users', 'ysws_eligible'):
        op.add_column('users', sa.Column('ysws_eligible', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    if column_exists('users', 'ysws_eligible'):
        op.drop_column('users', 'ysws_eligible')
    if column_exists('users', 'verification_status'):
        op.drop_column('users', 'verification_status')
