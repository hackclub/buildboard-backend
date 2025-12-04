"""Add GitHub integration fields

Revision ID: 4e18c15004df
Revises: a1396f016c3b
Create Date: 2025-11-23 00:04:24.412595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e18c15004df'
down_revision: Union[str, Sequence[str], None] = 'a1396f016c3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('github_installation_id', sa.String(length=100), nullable=True))
    op.add_column('projects', sa.Column('github_repo_path', sa.String(length=200), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'github_repo_path')
    op.drop_column('projects', 'github_installation_id')
