from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.campaign import Campaign


class CampaignEvent(Base):
    __tablename__ = "campaign_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    type: Mapped[str] = mapped_column(String(100), nullable=False)

    data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="campaign_events")
