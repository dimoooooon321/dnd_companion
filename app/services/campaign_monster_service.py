from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_monster import CampaignMonster
from app.models.monster import Monster
from app.services.campaign_service import get_campaign_for_user


def add_monster_to_campaign(
    db: Session,
    campaign_id: int,
    dm_id: int,
    monster_id: int,
    quantity: int = 1,
):
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.dm_id == dm_id)
        .first()
    )

    if campaign is None:
        campaign_exists = db.query(Campaign.id).filter(Campaign.id == campaign_id).first()
        if campaign_exists is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        raise HTTPException(status_code=403, detail="Only campaign DM can manage monsters")

    monster = db.query(Monster).filter(Monster.id == monster_id).first()

    if monster is None:
        raise HTTPException(status_code=404, detail="Monster not found")

    campaign_monster = (
        db.query(CampaignMonster)
        .filter(
            CampaignMonster.campaign_id == campaign_id,
            CampaignMonster.monster_id == monster_id,
        )
        .first()
    )

    if campaign_monster is None:
        campaign_monster = CampaignMonster(
            campaign_id=campaign_id,
            monster_id=monster_id,
            quantity=quantity,
        )
        db.add(campaign_monster)
    else:
        campaign_monster.quantity += quantity

    db.commit()
    db.refresh(campaign_monster)

    return campaign_monster


def get_campaign_monsters(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
):
    get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(CampaignMonster)
        .filter(CampaignMonster.campaign_id == campaign_id)
        .order_by(CampaignMonster.id)
        .all()
    )
