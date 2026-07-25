"""initial

Revision ID: 3dd5a89652cc
Revises:
Create Date: 2026-07-03 10:45:05.214236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3dd5a89652cc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline: all tables created by Base.metadata.create_all() in init_db()."""
    pass


def downgrade() -> None:
    pass
