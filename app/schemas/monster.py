from datetime import datetime

from pydantic import BaseModel


class MonsterCreate(BaseModel):
    name: str
    description: str
    hp: int
    armor_class: int
    challenge_rating: float
    image_url: str | None = None


class MonsterResponse(BaseModel):
    id: int
    created_by: int
    name: str
    description: str
    hp: int
    armor_class: int
    challenge_rating: float
    image_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
