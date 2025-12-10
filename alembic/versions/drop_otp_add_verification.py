"""Drop OTP table and add verification fields

Revision ID: drop_otp_add_verification
Revises: 67539c76e503
Create Date: 2025-12-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'drop_otp_add_verification'
down_revision: Union[str, Sequence[str], None] = 'afe9408d66b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'otps' in inspector.get_table_names():
        op.drop_table('otps')


def downgrade() -> None:
    op.create_table(
        'otps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_otps_email', 'otps', ['email'])
