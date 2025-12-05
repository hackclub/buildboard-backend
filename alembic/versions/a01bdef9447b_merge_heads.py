"""merge heads

Revision ID: a01bdef9447b
Revises: a1396f016c3b, c2f8a3b1d4e5
Create Date: 2025-12-05 11:02:01.837814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a01bdef9447b'
down_revision: Union[str, Sequence[str], None] = ('a1396f016c3b', 'c2f8a3b1d4e5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
