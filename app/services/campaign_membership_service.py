from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.character import Character


def add_character_to_campaign(
    db: Session,
    campaign_id: int,
    dm_id: int,
    character_id: int,
):
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.dm_id == dm_id)
        .first()
    )

    if campaign is None:
        campaign_exists = db.query(Campaign.id).filter(Campaign.id == campaign_id).first()
        if campaign_exists is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        raise HTTPException(status_code=403, detail="Only campaign DM can manage members")

    character = db.query(Character).filter(Character.id == character_id).first()

    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    membership = (
        db.query(CampaignMembership)
        .filter(
            CampaignMembership.campaign_id == campaign_id,
            CampaignMembership.character_id == character_id,
        )
        .first()
    )

    if membership is not None:
        return membership

    membership = CampaignMembership(
        campaign_id=campaign_id,
        character_id=character_id,
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership


def get_campaign_members(
    db: Session,
    campaign_id: int,
):
    return (
        db.query(Character)
        .join(CampaignMembership, CampaignMembership.character_id == Character.id)
        .filter(CampaignMembership.campaign_id == campaign_id)
        .order_by(Character.id)
        .all()
    )
