"""add referral_code fields

Revision ID: c2f8a3b1d4e5
Revises: 5786786c66e5
Create Date: 2025-12-05 12:00:00.000000

"""
from typing import Sequence, Union
import secrets
import string

from alembic import op
import sqlalchemy as sa


revision: str = 'c2f8a3b1d4e5'
down_revision: Union[str, Sequence[str], None] = '5786786c66e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generate_referral_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


def upgrade() -> None:
    op.add_column('users', sa.Column('referral_code', sa.String(8), nullable=True))
    op.add_column('users', sa.Column('referred_by', sa.String(8), nullable=True))
    
    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT user_id FROM users")).fetchall()
    for (user_id,) in users:
        code = generate_referral_code()
        conn.execute(
            sa.text("UPDATE users SET referral_code = :code WHERE user_id = :uid"),
            {"code": code, "uid": user_id}
        )
    
    op.alter_column('users', 'referral_code', nullable=False)
    op.create_index('ix_users_referral_code', 'users', ['referral_code'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_referral_code', table_name='users')
    op.drop_column('users', 'referred_by')
    op.drop_column('users', 'referral_code')
