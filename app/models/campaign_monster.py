from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.monster import Monster


class CampaignMonster(Base):
    __tablename__ = "campaign_monsters"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    monster_id: Mapped[int] = mapped_column(ForeignKey("monsters.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="campaign_monsters")
    monster: Mapped["Monster"] = relationship("Monster", back_populates="campaign_monsters")
