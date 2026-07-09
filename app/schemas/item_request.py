from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ItemRequestStatus = Literal["pending", "approved", "rejected"]


class ItemTransferRequestCreate(BaseModel):
    character_id: int
    item_id: int
    quantity: int = 1


class ItemTransferRequestResponse(BaseModel):
    id: int
    campaign_id: int
    character_id: int
    item_id: int
    quantity: int
    status: ItemRequestStatus
    requested_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True
