from pydantic import BaseModel

from app.schemas.campaign import CampaignResponse
from app.schemas.campaign_event import CampaignEventResponse
from app.schemas.campaign_monster import CampaignMonsterResponse
from app.schemas.campaign_scene import CampaignSceneResponse
from app.schemas.character import CharacterResponse


class BattleTokenStateResponse(BaseModel):
    id: int
    x: int
    y: int
    character_id: int | None
    monster_id: int | None

    class Config:
        from_attributes = True


class BattleMapStateResponse(BaseModel):
    id: int
    width: int
    height: int
    tokens: list[BattleTokenStateResponse]

    class Config:
        from_attributes = True


class CampaignStateResponse(BaseModel):
    campaign: CampaignResponse
    current_scene: CampaignSceneResponse | None
    characters: list[CharacterResponse]
    monsters: list[CampaignMonsterResponse]
    recent_events: list[CampaignEventResponse]
    battle_maps: list[BattleMapStateResponse]

    class Config:
        from_attributes = True
