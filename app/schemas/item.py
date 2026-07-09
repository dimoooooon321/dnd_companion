from datetime import datetime

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str
    item_type: str
    weight: float
    image_url: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    item_type: str
    weight: float
    image_url: str | None
    creator_id: int
    created_at: datetime

    class Config:
        from_attributes = True
