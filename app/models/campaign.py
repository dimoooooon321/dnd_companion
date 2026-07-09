from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.campaign_monster import CampaignMonster
    from app.models.user import User


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    dm_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    dm: Mapped["User"] = relationship("User")
    memberships: Mapped[list["CampaignMembership"]] = relationship(
        "CampaignMembership",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )

    campaign_monsters: Mapped[list["CampaignMonster"]] = relationship(
        "CampaignMonster",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )
