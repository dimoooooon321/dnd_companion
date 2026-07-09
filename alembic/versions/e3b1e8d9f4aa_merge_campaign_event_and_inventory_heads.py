"""merge campaign event and inventory heads

Revision ID: e3b1e8d9f4aa
Revises: 7c4b8f2d1a90, b1a7f8c4d2e9
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e3b1e8d9f4aa"
down_revision: Union[str, Sequence[str], None] = ("7c4b8f2d1a90", "b1a7f8c4d2e9")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
