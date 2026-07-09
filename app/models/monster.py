from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.campaign_monster import CampaignMonster
    from app.models.user import User


class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(primary_key=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    hp: Mapped[int] = mapped_column(nullable=False)

    armor_class: Mapped[int] = mapped_column(nullable=False)

    challenge_rating: Mapped[float] = mapped_column(Float, nullable=False)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship("User", back_populates="monsters")
    campaign_monsters: Mapped[list["CampaignMonster"]] = relationship(
        "CampaignMonster",
        back_populates="monster",
        cascade="all, delete-orphan",
    )
