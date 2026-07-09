"""add campaign events

Revision ID: b1a7f8c4d2e9
Revises: cc095daa3dc0
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1a7f8c4d2e9"
down_revision: Union[str, Sequence[str], None] = "cc095daa3dc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "campaign_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "campaign_id",
            sa.Integer(),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("campaign_events")
