from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id")
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    name: Mapped[str]

    race: Mapped[str]

    class_name: Mapped[str]

    level: Mapped[int] = mapped_column(
        default=1
    )

    max_hp: Mapped[int]

    current_hp: Mapped[int]