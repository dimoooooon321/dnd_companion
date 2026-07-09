from sqlalchemy.orm import Session, joinedload

from app.models.campaign_event import CampaignEvent
from app.models.campaign_membership import CampaignMembership
from app.models.campaign_monster import CampaignMonster
from app.models.character import Character
from app.services.campaign_service import get_campaign_for_user
from app.services.campaign_scene_service import get_current_campaign_scene

RECENT_CAMPAIGN_EVENTS_LIMIT = 10


def get_campaign_state(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
):
    campaign = get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )
    current_scene = get_current_campaign_scene(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    characters = (
        db.query(Character)
        .join(CampaignMembership, CampaignMembership.character_id == Character.id)
        .filter(CampaignMembership.campaign_id == campaign_id)
        .order_by(CampaignMembership.id)
        .all()
    )

    monsters = (
        db.query(CampaignMonster)
        .options(joinedload(CampaignMonster.monster))
        .filter(CampaignMonster.campaign_id == campaign_id)
        .order_by(CampaignMonster.id)
        .all()
    )

    recent_events = (
        db.query(CampaignEvent)
        .filter(CampaignEvent.campaign_id == campaign_id)
        .order_by(CampaignEvent.id.desc())
        .limit(RECENT_CAMPAIGN_EVENTS_LIMIT)
        .all()
    )
    recent_events.reverse()

    return {
        "campaign": campaign,
        "current_scene": current_scene,
        "characters": characters,
        "monsters": monsters,
        "recent_events": recent_events,
    }
