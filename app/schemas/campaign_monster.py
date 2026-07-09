from datetime import datetime

from pydantic import BaseModel

from app.schemas.monster import MonsterResponse


class CampaignMonsterCreate(BaseModel):
    monster_id: int
    quantity: int = 1


class CampaignMonsterResponse(BaseModel):
    id: int
    campaign_id: int
    monster_id: int
    quantity: int
    created_at: datetime
    monster: MonsterResponse

    class Config:
        from_attributes = True
