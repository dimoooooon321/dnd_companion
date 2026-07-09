from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.battle_map import BattleMap
    from app.models.character import Character
    from app.models.monster import Monster


class BattleToken(Base):
    __tablename__ = "battle_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    battle_map_id: Mapped[int] = mapped_column(ForeignKey("battle_maps.id"), nullable=False)

    token_type: Mapped[str] = mapped_column(String(20), nullable=False)

    character_id: Mapped[int | None] = mapped_column(ForeignKey("characters.id"), nullable=True)

    monster_id: Mapped[int | None] = mapped_column(ForeignKey("monsters.id"), nullable=True)

    x: Mapped[int] = mapped_column(Integer, nullable=False)

    y: Mapped[int] = mapped_column(Integer, nullable=False)

    battle_map: Mapped["BattleMap"] = relationship("BattleMap", back_populates="tokens")
    character: Mapped["Character | None"] = relationship("Character", back_populates="battle_tokens")
    monster: Mapped["Monster | None"] = relationship("Monster", back_populates="battle_tokens")
