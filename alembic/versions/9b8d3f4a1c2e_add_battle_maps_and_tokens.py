"""add battle maps and tokens

Revision ID: 9b8d3f4a1c2e
Revises: 9f2b6a2d4c11
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b8d3f4a1c2e"
down_revision: Union[str, Sequence[str], None] = "9f2b6a2d4c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "battle_maps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "battle_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("battle_map_id", sa.Integer(), nullable=False),
        sa.Column("token_type", sa.String(length=20), nullable=False),
        sa.Column("character_id", sa.Integer(), nullable=True),
        sa.Column("monster_id", sa.Integer(), nullable=True),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["battle_map_id"], ["battle_maps.id"]),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["monster_id"], ["monsters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("battle_tokens")
    op.drop_table("battle_maps")
