from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    race: Mapped[str] = mapped_column(
        String(50)
    )

    class_name: Mapped[str] = mapped_column(
        String(50)
    )

    level: Mapped[int] = mapped_column(
        default=1
    )

    experience: Mapped[int] = mapped_column(
        default=0
    )

    max_hp: Mapped[int]

    current_hp: Mapped[int]


    strength: Mapped[int]
    dexterity: Mapped[int]
    constitution: Mapped[int]
    intelligence: Mapped[int]
    wisdom: Mapped[int]
    charisma: Mapped[int]