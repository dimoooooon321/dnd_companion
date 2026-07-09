from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.battle_map import BattleMap
from app.models.campaign import Campaign
from app.services.campaign_service import get_campaign_for_user


def _get_campaign_for_dm(db: Session, campaign_id: int, user_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.dm_id != user_id:
        raise HTTPException(status_code=403, detail="Only campaign DM can manage battle maps")

    return campaign


def _get_battle_map(db: Session, map_id: int) -> BattleMap:
    battle_map = db.query(BattleMap).filter(BattleMap.id == map_id).first()
    if battle_map is None:
        raise HTTPException(status_code=404, detail="Battle map not found")
    return battle_map


def create_battle_map(
    db: Session,
    campaign_id: int,
    user_id: int,
    name: str,
    width: int,
    height: int,
) -> BattleMap:
    if width < 1 or height < 1:
        raise HTTPException(status_code=400, detail="Battle map dimensions must be at least 1")

    _get_campaign_for_dm(db=db, campaign_id=campaign_id, user_id=user_id)

    battle_map = BattleMap(
        campaign_id=campaign_id,
        name=name,
        width=width,
        height=height,
    )
    db.add(battle_map)
    db.commit()
    db.refresh(battle_map)
    return battle_map


def get_battle_maps_for_campaign(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
) -> list[BattleMap]:
    get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(BattleMap)
        .filter(BattleMap.campaign_id == campaign_id)
        .order_by(BattleMap.id)
        .all()
    )


def get_battle_map_for_user(
    db: Session,
    map_id: int,
    user_id: int,
    role: str,
) -> BattleMap:
    battle_map = _get_battle_map(db=db, map_id=map_id)

    get_campaign_for_user(
        db=db,
        campaign_id=battle_map.campaign_id,
        user_id=user_id,
        role=role,
    )

    return battle_map


def delete_battle_map(
    db: Session,
    map_id: int,
    user_id: int,
) -> None:
    battle_map = _get_battle_map(db=db, map_id=map_id)
    _get_campaign_for_dm(db=db, campaign_id=battle_map.campaign_id, user_id=user_id)

    db.delete(battle_map)
    db.commit()
