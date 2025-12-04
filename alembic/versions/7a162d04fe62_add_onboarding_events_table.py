"""add_onboarding_events_table

Revision ID: 7a162d04fe62
Revises: 1610370bd845
Create Date: 2025-12-03 10:56:42.030198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7a162d04fe62'
down_revision: Union[str, Sequence[str], None] = '1610370bd845'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('onboarding_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('event', sa.String(length=50), nullable=False),
        sa.Column('slide', sa.Integer(), nullable=True),
        sa.Column('total_slides', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_onboarding_events_id'), 'onboarding_events', ['id'], unique=False)
    op.create_index(op.f('ix_onboarding_events_user_id'), 'onboarding_events', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_onboarding_events_user_id'), table_name='onboarding_events')
    op.drop_index(op.f('ix_onboarding_events_id'), table_name='onboarding_events')
    op.drop_table('onboarding_events')
