from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.battle_map import BattleMap
from app.models.battle_token import BattleToken
from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.campaign_monster import CampaignMonster
from app.models.character import Character
from app.models.monster import Monster
from app.services.campaign_event_service import broadcast_campaign_event
from app.services.campaign_service import get_campaign_for_user


def _get_battle_map(db: Session, map_id: int) -> BattleMap:
    battle_map = db.query(BattleMap).filter(BattleMap.id == map_id).first()
    if battle_map is None:
        raise HTTPException(status_code=404, detail="Battle map not found")
    return battle_map


def _get_campaign_for_dm(db: Session, campaign_id: int, user_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.dm_id != user_id:
        raise HTTPException(status_code=403, detail="Only campaign DM can manage battle tokens")

    return campaign


def _validate_token_target(
    db: Session,
    battle_map: BattleMap,
    token_type: str,
    character_id: int | None,
    monster_id: int | None,
) -> tuple[int | None, int | None]:
    if token_type == "character":
        if character_id is None or monster_id is not None:
            raise HTTPException(status_code=400, detail="Character tokens must reference only a character")

        character = db.query(Character).filter(Character.id == character_id).first()
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")

        membership = (
            db.query(CampaignMembership.id)
            .filter(
                CampaignMembership.campaign_id == battle_map.campaign_id,
                CampaignMembership.character_id == character_id,
            )
            .first()
        )
        if membership is None:
            raise HTTPException(status_code=404, detail="Character not found in campaign")

        return character_id, None

    if token_type == "monster":
        if monster_id is None or character_id is not None:
            raise HTTPException(status_code=400, detail="Monster tokens must reference only a monster")

        monster = db.query(Monster).filter(Monster.id == monster_id).first()
        if monster is None:
            raise HTTPException(status_code=404, detail="Monster not found")

        campaign_monster = (
            db.query(CampaignMonster.id)
            .filter(
                CampaignMonster.campaign_id == battle_map.campaign_id,
                CampaignMonster.monster_id == monster_id,
            )
            .first()
        )
        if campaign_monster is None:
            raise HTTPException(status_code=404, detail="Monster not found in campaign")

        return None, monster_id

    raise HTTPException(status_code=400, detail="Invalid token type")


def create_battle_token(
    db: Session,
    map_id: int,
    user_id: int,
    token_type: str,
    character_id: int | None,
    monster_id: int | None,
    x: int,
    y: int,
) -> BattleToken:
    battle_map = _get_battle_map(db=db, map_id=map_id)
    _get_campaign_for_dm(db=db, campaign_id=battle_map.campaign_id, user_id=user_id)

    resolved_character_id, resolved_monster_id = _validate_token_target(
        db=db,
        battle_map=battle_map,
        token_type=token_type,
        character_id=character_id,
        monster_id=monster_id,
    )

    token = BattleToken(
        battle_map_id=map_id,
        token_type=token_type,
        character_id=resolved_character_id,
        monster_id=resolved_monster_id,
        x=x,
        y=y,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_battle_tokens_for_map(
    db: Session,
    map_id: int,
    user_id: int,
    role: str,
) -> list[BattleToken]:
    battle_map = _get_battle_map(db=db, map_id=map_id)

    get_campaign_for_user(
        db=db,
        campaign_id=battle_map.campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(BattleToken)
        .filter(BattleToken.battle_map_id == map_id)
        .order_by(BattleToken.id)
        .all()
    )


def move_battle_token(
    db: Session,
    token_id: int,
    user_id: int,
    x: int,
    y: int,
) -> BattleToken:
    token = (
        db.query(BattleToken)
        .options(joinedload(BattleToken.battle_map).joinedload(BattleMap.campaign))
        .filter(BattleToken.id == token_id)
        .first()
    )
    if token is None:
        raise HTTPException(status_code=404, detail="Battle token not found")

    battle_map = token.battle_map
    campaign = battle_map.campaign if battle_map is not None else None
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.dm_id != user_id:
        raise HTTPException(status_code=403, detail="Only campaign DM can move battle tokens")

    old_x = token.x
    old_y = token.y
    token.x = x
    token.y = y

    broadcast_campaign_event(
        db=db,
        campaign_id=campaign.id,
        event_type="token_moved",
        data={
            "token_id": token.id,
            "old_x": old_x,
            "old_y": old_y,
            "new_x": x,
            "new_y": y,
        },
        websocket_data={
            "token_id": token.id,
            "x": x,
            "y": y,
        },
    )

    db.refresh(token)
    return token
