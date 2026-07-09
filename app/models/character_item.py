from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.item import Item


class CharacterItem(Base):
    __tablename__ = "character_items"
    __table_args__ = (
        UniqueConstraint("character_id", "item_id", name="uq_character_items_character_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    character: Mapped["Character"] = relationship("Character")
    item: Mapped["Item"] = relationship("Item", back_populates="character_items")
