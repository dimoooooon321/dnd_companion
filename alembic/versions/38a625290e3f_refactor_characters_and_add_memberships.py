"""refactor characters and add memberships

Revision ID: 38a625290e3f
Revises: cc095daa3dc0
Create Date: 2026-07-08 20:55:08.526513

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38a625290e3f'
down_revision: Union[str, Sequence[str], None] = 'cc095daa3dc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Создаём таблицу связей персонажей и кампаний
    op.create_table(
        'campaign_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(
            ['campaign_id'],
            ['campaigns.id']
        ),

        sa.ForeignKeyConstraint(
            ['character_id'],
            ['characters.id']
        ),

        sa.PrimaryKeyConstraint('id')
    )


    # Добавляем опыт
    op.add_column(
        'characters',
        sa.Column(
            'experience',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )


    # Добавляем характеристики
    op.add_column(
        'characters',
        sa.Column(
            'strength',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )

    op.add_column(
        'characters',
        sa.Column(
            'dexterity',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )

    op.add_column(
        'characters',
        sa.Column(
            'constitution',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )

    op.add_column(
        'characters',
        sa.Column(
            'intelligence',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )

    op.add_column(
        'characters',
        sa.Column(
            'wisdom',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )

    op.add_column(
        'characters',
        sa.Column(
            'charisma',
            sa.Integer(),
            nullable=False,
            server_default='10'
        )
    )


    # Убираем старую привязку персонажа к одной кампании
    op.drop_constraint(
        op.f('characters_campaign_id_fkey'),
        'characters',
        type_='foreignkey'
    )

    op.drop_column(
        'characters',
        'campaign_id'
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Возвращаем campaign_id обратно
    op.add_column(
        'characters',
        sa.Column(
            'campaign_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=True
        )
    )

    op.create_foreign_key(
        op.f('characters_campaign_id_fkey'),
        'characters',
        'campaigns',
        ['campaign_id'],
        ['id']
    )


    # Удаляем новые поля
    op.drop_column(
        'characters',
        'charisma'
    )

    op.drop_column(
        'characters',
        'wisdom'
    )

    op.drop_column(
        'characters',
        'intelligence'
    )

    op.drop_column(
        'characters',
        'constitution'
    )

    op.drop_column(
        'characters',
        'dexterity'
    )

    op.drop_column(
        'characters',
        'strength'
    )

    op.drop_column(
        'characters',
        'experience'
    )


    # Удаляем таблицу связей
    op.drop_table(
        'campaign_memberships'
    )