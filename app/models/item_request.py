from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.character import Character
    from app.models.item import Item


class ItemTransferRequest(Base):
    __tablename__ = "item_transfer_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    requested_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped["Campaign"] = relationship("Campaign")
    character: Mapped["Character"] = relationship("Character")
    item: Mapped["Item"] = relationship("Item", back_populates="transfer_requests")
