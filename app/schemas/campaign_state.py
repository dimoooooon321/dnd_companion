from pydantic import BaseModel

from app.schemas.campaign import CampaignResponse
from app.schemas.campaign_event import CampaignEventResponse
from app.schemas.campaign_monster import CampaignMonsterResponse
from app.schemas.campaign_scene import CampaignSceneResponse
from app.schemas.character import CharacterResponse


class CampaignStateResponse(BaseModel):
    campaign: CampaignResponse
    current_scene: CampaignSceneResponse | None
    characters: list[CharacterResponse]
    monsters: list[CampaignMonsterResponse]
    recent_events: list[CampaignEventResponse]

    class Config:
        from_attributes = True
