"""add identity vault fields

Revision ID: add_idv_fields
Revises: 182d039e6e58
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_idv_fields'
down_revision: Union[str, Sequence[str], None] = '182d039e6e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('identity_vault_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('identity_vault_access_token', sa.String(512), nullable=True))
    op.add_column('users', sa.Column('idv_country', sa.String(10), nullable=True))
    
    op.create_index('ix_users_identity_vault_id', 'users', ['identity_vault_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_identity_vault_id', table_name='users')
    op.drop_column('users', 'idv_country')
    op.drop_column('users', 'identity_vault_access_token')
    op.drop_column('users', 'identity_vault_id')
