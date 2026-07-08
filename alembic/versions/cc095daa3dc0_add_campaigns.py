"""add campaigns

Revision ID: cc095daa3dc0
Revises: 09831a672b0c
Create Date: 2026-07-08 19:28:31.051815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc095daa3dc0'
down_revision: Union[str, Sequence[str], None] = '09831a672b0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'campaigns',
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False
        )
    )

    op.alter_column(
        'campaigns',
        'description',
        existing_type=sa.VARCHAR(),
        type_=sa.Text(),
        nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.alter_column(
        'campaigns',
        'description',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(),
        nullable=False
    )

    op.drop_column(
        'campaigns',
        'created_at'
    )
