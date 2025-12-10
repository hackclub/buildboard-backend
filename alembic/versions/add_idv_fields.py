"""add identity vault fields

Revision ID: add_idv_fields
Revises: 182d039e6e58
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'add_idv_fields'
down_revision: Union[str, Sequence[str], None] = '182d039e6e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    if not column_exists('users', 'identity_vault_id'):
        op.add_column('users', sa.Column('identity_vault_id', sa.String(255), nullable=True))
    if not column_exists('users', 'identity_vault_access_token'):
        op.add_column('users', sa.Column('identity_vault_access_token', sa.String(512), nullable=True))
    if not column_exists('users', 'idv_country'):
        op.add_column('users', sa.Column('idv_country', sa.String(10), nullable=True))
    
    if not index_exists('users', 'ix_users_identity_vault_id'):
        op.create_index('ix_users_identity_vault_id', 'users', ['identity_vault_id'], unique=True)


def downgrade() -> None:
    if index_exists('users', 'ix_users_identity_vault_id'):
        op.drop_index('ix_users_identity_vault_id', table_name='users')
    if column_exists('users', 'idv_country'):
        op.drop_column('users', 'idv_country')
    if column_exists('users', 'identity_vault_access_token'):
        op.drop_column('users', 'identity_vault_access_token')
    if column_exists('users', 'identity_vault_id'):
        op.drop_column('users', 'identity_vault_id')
