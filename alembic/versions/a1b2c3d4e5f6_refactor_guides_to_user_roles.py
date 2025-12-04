"""refactor_guides_to_user_roles

Revision ID: a1b2c3d4e5f6
Revises: 37cf8e418e04
Create Date: 2025-12-04 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '37cf8e418e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to users table
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('assigned_author_id', sa.String(length=36), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_assigned_author_id'), 'users', ['assigned_author_id'], unique=False)
    
    # Create self-referential foreign key
    op.create_foreign_key('fk_users_assigned_author_id', 'users', 'users', ['assigned_author_id'], ['user_id'])
    
    # Drop old guide_id foreign key and column
    op.drop_constraint('users_guide_id_fkey', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_guide_id'), table_name='users')
    op.drop_column('users', 'guide_id')
    
    # Drop guides table
    op.drop_index(op.f('ix_guides_slack_id'), table_name='guides')
    op.drop_index(op.f('ix_guides_guide_id'), table_name='guides')
    op.drop_table('guides')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate guides table
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
    
    # Recreate guide_id on users
    op.add_column('users', sa.Column('guide_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_users_guide_id'), 'users', ['guide_id'], unique=False)
    op.create_foreign_key('fk_users_guide_id', 'users', 'guides', ['guide_id'], ['guide_id'])
    
    # Drop new columns
    op.drop_constraint('fk_users_assigned_author_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_assigned_author_id'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'assigned_author_id')
    op.drop_column('users', 'role')
