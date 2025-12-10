"""auto_migration

Revision ID: 67539c76e503
Revises: add_idv_fields
Create Date: 2025-12-08 10:03:23.430678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67539c76e503'
down_revision: Union[str, Sequence[str], None] = 'add_idv_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not table_exists(table_name):
        return False
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    """Upgrade schema."""
    if table_exists('otps'):
        if index_exists('otps', 'ix_otps_email'):
            op.drop_index(op.f('ix_otps_email'), table_name='otps')
        op.drop_table('otps')


def downgrade() -> None:
    """Downgrade schema."""
    if not table_exists('otps'):
        op.create_table('otps',
            sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
            sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
            sa.Column('code', sa.VARCHAR(length=6), autoincrement=False, nullable=False),
            sa.Column('used', sa.BOOLEAN(), autoincrement=False, nullable=False),
            sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
            sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
            sa.PrimaryKeyConstraint('id', name=op.f('otps_pkey'))
        )
        op.create_index(op.f('ix_otps_email'), 'otps', ['email'], unique=False)
