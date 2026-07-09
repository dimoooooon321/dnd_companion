from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.battle_token import BattleTokenResponse


class BattleMapCreate(BaseModel):
    name: str
    width: int
    height: int


class BattleMapResponse(BaseModel):
    id: int
    campaign_id: int
    name: str
    width: int
    height: int
    created_at: datetime
    tokens: list[BattleTokenResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
