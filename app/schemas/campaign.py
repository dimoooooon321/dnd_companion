from datetime import datetime

from pydantic import BaseModel


class CampaignCreate(BaseModel):

    name: str
    description: str | None = None



class CampaignResponse(BaseModel):

    id: int
    name: str
    description: str | None
    dm_id: int
    created_at: datetime


    class Config:
        from_attributes = True