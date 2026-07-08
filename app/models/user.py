from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.character import Character


class UserRole(str, Enum):
    DM = "dm"
    PLAYER = "player"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[str] = mapped_column(default=UserRole.PLAYER)

    is_active: Mapped[bool] = mapped_column(default=True)

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="owner",
        cascade="all, delete-orphan"
    )