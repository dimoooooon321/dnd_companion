from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_scene import CampaignScene
from app.services.campaign_event_service import broadcast_campaign_event
from app.services.campaign_service import get_campaign_for_user


def _get_campaign_for_dm(db: Session, campaign_id: int, user_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.dm_id != user_id:
        raise HTTPException(status_code=403, detail="Only campaign DM can manage scenes")

    return campaign


def _serialize_scene(scene: CampaignScene) -> dict[str, object]:
    return {
        "scene_id": scene.id,
        "campaign_id": scene.campaign_id,
        "title": scene.title,
        "description": scene.description,
        "image_url": scene.image_url,
        "is_active": scene.is_active,
    }


def create_campaign_scene(
    db: Session,
    campaign_id: int,
    user_id: int,
    title: str,
    description: str,
    image_url: str | None = None,
) -> CampaignScene:
    _get_campaign_for_dm(db=db, campaign_id=campaign_id, user_id=user_id)

    scene = CampaignScene(
        campaign_id=campaign_id,
        title=title,
        description=description,
        image_url=image_url,
        is_active=False,
    )
    db.add(scene)
    db.commit()
    db.refresh(scene)
    return scene


def get_campaign_scenes(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
) -> list[CampaignScene]:
    get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(CampaignScene)
        .filter(CampaignScene.campaign_id == campaign_id)
        .order_by(CampaignScene.created_at, CampaignScene.id)
        .all()
    )


def get_current_campaign_scene(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
) -> CampaignScene | None:
    get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(CampaignScene)
        .filter(
            CampaignScene.campaign_id == campaign_id,
            CampaignScene.is_active.is_(True),
        )
        .order_by(CampaignScene.id.desc())
        .first()
    )


def activate_campaign_scene(
    db: Session,
    campaign_id: int,
    scene_id: int,
    user_id: int,
) -> CampaignScene:
    _get_campaign_for_dm(db=db, campaign_id=campaign_id, user_id=user_id)

    scene = (
        db.query(CampaignScene)
        .filter(
            CampaignScene.id == scene_id,
            CampaignScene.campaign_id == campaign_id,
        )
        .first()
    )
    if scene is None:
        raise HTTPException(status_code=404, detail="Scene not found")

    db.query(CampaignScene).filter(CampaignScene.campaign_id == campaign_id).update(
        {CampaignScene.is_active: False},
        synchronize_session=False,
    )
    scene.is_active = True
    db.add(scene)
    db.commit()
    db.refresh(scene)

    broadcast_campaign_event(
        db=db,
        campaign_id=campaign_id,
        event_type="scene_changed",
        data=_serialize_scene(scene),
    )

    return scene
