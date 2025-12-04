"""add_guides_table_and_user_guide_id

Revision ID: 37cf8e418e04
Revises: 52a393387140
Create Date: 2025-12-04 12:05:03.484274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '37cf8e418e04'
down_revision: Union[str, Sequence[str], None] = '52a393387140'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create guides table
    op.create_table('guides',
        sa.Column('guide_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slack_id', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('guide_id')
    )
    op.create_index(op.f('ix_guides_guide_id'), 'guides', ['guide_id'], unique=False)
    op.create_index(op.f('ix_guides_slack_id'), 'guides', ['slack_id'], unique=True)

    # Add guide_id column to users table
    op.add_column('users', sa.Column('guide_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_users_guide_id'), 'users', ['guide_id'], unique=False)
    op.create_foreign_key('fk_users_guide_id', 'users', 'guides', ['guide_id'], ['guide_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove guide_id from users
    op.drop_constraint('fk_users_guide_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_guide_id'), table_name='users')
    op.drop_column('users', 'guide_id')

    # Drop guides table
    op.drop_index(op.f('ix_guides_slack_id'), table_name='guides')
    op.drop_index(op.f('ix_guides_guide_id'), table_name='guides')
    op.drop_table('guides')
