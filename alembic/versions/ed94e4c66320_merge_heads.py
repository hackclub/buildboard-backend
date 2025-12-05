"""merge heads

Revision ID: ed94e4c66320
Revises: a1b2c3d4e5f6, b1639e2cf5fe
Create Date: 2025-12-05 11:34:44.092659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed94e4c66320'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'b1639e2cf5fe')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
