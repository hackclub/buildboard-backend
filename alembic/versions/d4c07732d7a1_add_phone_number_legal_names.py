"""add_phone_number_legal_names

Revision ID: d4c07732d7a1
Revises: drop_otp_add_verification
Create Date: 2025-12-09 09:01:52.980743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4c07732d7a1'
down_revision: Union[str, Sequence[str], None] = 'drop_otp_add_verification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number')
