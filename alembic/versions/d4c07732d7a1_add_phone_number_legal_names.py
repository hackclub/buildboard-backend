"""add_phone_number_legal_names

Revision ID: d4c07732d7a1
Revises: drop_otp_add_verification
Create Date: 2025-12-09 09:01:52.980743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'd4c07732d7a1'
down_revision: Union[str, Sequence[str], None] = 'drop_otp_add_verification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Upgrade schema."""
    if not column_exists('users', 'phone_number'):
        op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    if column_exists('users', 'phone_number'):
        op.drop_column('users', 'phone_number')
