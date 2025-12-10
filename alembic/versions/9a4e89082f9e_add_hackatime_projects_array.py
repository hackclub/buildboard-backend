"""add_hackatime_projects_array

Revision ID: 9a4e89082f9e
Revises: d4c07732d7a1
Create Date: 2025-12-09 09:14:45.922768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a4e89082f9e'
down_revision: Union[str, Sequence[str], None] = 'd4c07732d7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('hackatime_projects', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('projects', sa.Column('hackatime_hours', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'hackatime_hours')
    op.drop_column('projects', 'hackatime_projects')
