"""merge_heads

Revision ID: 1610370bd845
Revises: 843f222ad642, 86d6b6532536
Create Date: 2025-12-03 10:56:31.085657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1610370bd845'
down_revision: Union[str, Sequence[str], None] = ('843f222ad642', '86d6b6532536')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
