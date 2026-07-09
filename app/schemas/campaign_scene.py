from datetime import datetime

from pydantic import BaseModel


class CampaignSceneCreate(BaseModel):
    title: str
    description: str
    image_url: str | None = None


class CampaignSceneResponse(BaseModel):
    id: int
    campaign_id: int
    title: str
    description: str
    image_url: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
