from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.battle_token import BattleToken
    from app.models.campaign import Campaign


class BattleMap(Base):
    __tablename__ = "battle_maps"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    width: Mapped[int] = mapped_column(Integer, nullable=False)

    height: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="battle_maps")
    tokens: Mapped[list["BattleToken"]] = relationship(
        "BattleToken",
        back_populates="battle_map",
        cascade="all, delete-orphan",
    )
