from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, Enum):
    DM = "dm"
    PLAYER = "player"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str]

    role: Mapped[str] = mapped_column(
        default=UserRole.PLAYER
    )

    is_active: Mapped[bool] = mapped_column(
        default=True
    )