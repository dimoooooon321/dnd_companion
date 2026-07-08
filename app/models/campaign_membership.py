from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CampaignMembership(Base):
    __tablename__ = "campaign_memberships"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False)

    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="memberships")
    character: Mapped["Character"] = relationship("Character", back_populates="memberships")