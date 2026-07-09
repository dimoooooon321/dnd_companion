from datetime import datetime

from pydantic import BaseModel


class CampaignEventResponse(BaseModel):
    id: int
    campaign_id: int
    type: str
    data: dict[str, object]
    created_at: datetime

    class Config:
        from_attributes = True
