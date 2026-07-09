from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.character_item import CharacterItem
    from app.models.item_request import ItemTransferRequest
    from app.models.user import User


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    item_type: Mapped[str] = mapped_column(String(100), nullable=False)

    weight: Mapped[float] = mapped_column(Float, nullable=False)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship("User")
    character_items: Mapped[list["CharacterItem"]] = relationship(
        "CharacterItem",
        back_populates="item",
        cascade="all, delete-orphan",
    )
    transfer_requests: Mapped[list["ItemTransferRequest"]] = relationship(
        "ItemTransferRequest",
        back_populates="item",
        cascade="all, delete-orphan",
    )
