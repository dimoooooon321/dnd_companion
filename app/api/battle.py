from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.battle_map import BattleMapResponse
from app.schemas.battle_token import BattleTokenCreate, BattleTokenMove, BattleTokenResponse
from app.services.battle_map_service import (
    delete_battle_map,
    get_battle_map_for_user,
)
from app.services.battle_token_service import (
    create_battle_token,
    get_battle_tokens_for_map,
    move_battle_token,
)


router = APIRouter()
battle_maps_router = APIRouter(prefix="/battle-maps", tags=["Battle Maps"])
battle_tokens_router = APIRouter(prefix="/battle-tokens", tags=["Battle Tokens"])


@battle_maps_router.get(
    "/{map_id}",
    response_model=BattleMapResponse,
)
def get_battle_map_endpoint(
    map_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_battle_map_for_user(
        db=db,
        map_id=map_id,
        user_id=user.id,
        role=user.role,
    )


@battle_maps_router.delete(
    "/{map_id}",
)
def delete_battle_map_endpoint(
    map_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_battle_map(
        db=db,
        map_id=map_id,
        user_id=user.id,
    )
    return {"status": "ok"}


@battle_maps_router.post(
    "/{map_id}/tokens",
    response_model=BattleTokenResponse,
)
def create_battle_token_endpoint(
    map_id: int,
    payload: BattleTokenCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_battle_token(
        db=db,
        map_id=map_id,
        user_id=user.id,
        token_type=payload.token_type,
        character_id=payload.character_id,
        monster_id=payload.monster_id,
        x=payload.x,
        y=payload.y,
    )


@battle_maps_router.get(
    "/{map_id}/tokens",
    response_model=list[BattleTokenResponse],
)
def get_battle_tokens_endpoint(
    map_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_battle_tokens_for_map(
        db=db,
        map_id=map_id,
        user_id=user.id,
        role=user.role,
    )


@battle_tokens_router.patch(
    "/{token_id}",
    response_model=BattleTokenResponse,
)
def move_battle_token_endpoint(
    token_id: int,
    payload: BattleTokenMove,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return move_battle_token(
        db=db,
        token_id=token_id,
        user_id=user.id,
        x=payload.x,
        y=payload.y,
    )


router.include_router(battle_maps_router)
router.include_router(battle_tokens_router)
