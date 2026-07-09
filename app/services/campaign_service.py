from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.character import Character


def create_campaign(
    db: Session,
    user_id: int,
    name: str,
    description: str | None = None,
):
    campaign = Campaign(
        name=name,
        description=description,
        dm_id=user_id,
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return campaign


def get_campaigns_for_user(
    db: Session,
    user_id: int,
    role: str,
):
    query = db.query(Campaign)

    if role == "dm":
        return query.filter(Campaign.dm_id == user_id).order_by(Campaign.id).all()

    return (
        query.join(CampaignMembership, CampaignMembership.campaign_id == Campaign.id)
        .join(Character, Character.id == CampaignMembership.character_id)
        .filter(Character.owner_id == user_id)
        .order_by(Campaign.id)
        .distinct()
        .all()
    )


def get_campaign_for_user(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if role == "dm":
        if campaign.dm_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this campaign",
            )

        return campaign

    has_access = (
        db.query(CampaignMembership.id)
        .join(Character, Character.id == CampaignMembership.character_id)
        .filter(
            CampaignMembership.campaign_id == campaign_id,
            Character.owner_id == user_id,
        )
        .first()
        is not None
    )

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this campaign",
        )

    return campaign
