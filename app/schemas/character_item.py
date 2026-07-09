from pydantic import BaseModel

from app.schemas.item import ItemResponse


class CharacterItemResponse(BaseModel):
    id: int
    character_id: int
    item_id: int
    quantity: int
    item: ItemResponse

    class Config:
        from_attributes = True
