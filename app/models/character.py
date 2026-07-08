from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    race: Mapped[str] = mapped_column(String(50), nullable=False)

    class_name: Mapped[str] = mapped_column(String(50), nullable=False)

    level: Mapped[int] = mapped_column(default=1)

    experience: Mapped[int] = mapped_column(default=0)

    max_hp: Mapped[int] = mapped_column(nullable=False)

    current_hp: Mapped[int] = mapped_column(nullable=False)

    strength: Mapped[int] = mapped_column(default=10)
    dexterity: Mapped[int] = mapped_column(default=10)
    constitution: Mapped[int] = mapped_column(default=10)
    intelligence: Mapped[int] = mapped_column(default=10)
    wisdom: Mapped[int] = mapped_column(default=10)
    charisma: Mapped[int] = mapped_column(default=10)

    owner: Mapped["User"] = relationship("User", back_populates="characters")
    memberships: Mapped[list["CampaignMembership"]] = relationship(
        "CampaignMembership",
        back_populates="character",
        cascade="all, delete-orphan"
    )