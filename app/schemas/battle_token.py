from typing import Literal

from pydantic import BaseModel


class BattleTokenCreate(BaseModel):
    token_type: Literal["character", "monster"]
    character_id: int | None = None
    monster_id: int | None = None
    x: int
    y: int


class BattleTokenMove(BaseModel):
    x: int
    y: int


class BattleTokenResponse(BaseModel):
    id: int
    battle_map_id: int
    token_type: str
    character_id: int | None
    monster_id: int | None
    x: int
    y: int

    class Config:
        from_attributes = True
