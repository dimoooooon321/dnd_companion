from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CampaignMembership(Base):
    __tablename__ = "campaign_memberships"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id")
    )


    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id")
    )


    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )