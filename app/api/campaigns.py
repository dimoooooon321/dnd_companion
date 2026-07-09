from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.campaign_event import CampaignEventResponse
from app.schemas.campaign_monster import (
    CampaignMonsterCreate,
    CampaignMonsterResponse,
)
from app.schemas.campaign_scene import CampaignSceneCreate, CampaignSceneResponse
from app.schemas.campaign_membership import CampaignMembershipCreate
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse
)
from app.schemas.campaign_state import CampaignStateResponse
from app.schemas.character import CharacterHpUpdate, CharacterResponse
from app.schemas.item_request import ItemTransferRequestCreate, ItemTransferRequestResponse
from app.services.campaign_event_service import broadcast_campaign_event
from app.services.campaign_event_service import get_campaign_events

from app.api.dependencies import get_current_user
from app.services.campaign_service import (
    create_campaign as create_campaign_service,
    get_campaign_for_user,
    get_campaigns_for_user,
)
from app.services.campaign_membership_service import (
    add_character_to_campaign,
    get_campaign_members,
)
from app.services.campaign_monster_service import (
    add_monster_to_campaign,
    get_campaign_monsters,
)
from app.services.campaign_scene_service import (
    activate_campaign_scene,
    create_campaign_scene,
    get_campaign_scenes,
    get_current_campaign_scene,
)
from app.services.campaign_state_service import get_campaign_state
from app.services.item_request_service import (
    create_item_request as create_item_request_service,
    get_item_requests_for_campaign as get_item_requests_for_campaign_service,
)
from pydantic import BaseModel
from app.services.character_service import update_character_hp

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


class CampaignSystemEventCreate(BaseModel):
    type: str
    text: str


@router.get(
    "/",
    response_model=list[CampaignResponse],
)
def list_campaigns(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaigns_for_user(
        db=db,
        user_id=user.id,
        role=user.role,
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.get(
    "/{campaign_id}/state",
    response_model=CampaignStateResponse,
)
def get_campaign_state_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaign_state(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )



@router.post(
    "/",
    response_model=CampaignResponse
)
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != "dm":
        raise HTTPException(
            status_code=403,
            detail="Only DM can create campaigns"
        )

    return create_campaign_service(
        db=db,
        user_id=user.id,
        name=campaign.name,
        description=campaign.description,
    )


@router.post(
    "/{campaign_id}/members",
)
def add_campaign_member(
    campaign_id: int,
    payload: CampaignMembershipCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return add_character_to_campaign(
        db=db,
        campaign_id=campaign_id,
        dm_id=user.id,
        character_id=payload.character_id,
    )


@router.get(
    "/{campaign_id}/members",
    response_model=list[CharacterResponse],
)
def get_campaign_members_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.dm_id != user.id:
        raise HTTPException(status_code=403, detail="Only campaign DM can view members")

    return get_campaign_members(
        db=db,
        campaign_id=campaign_id,
    )


@router.post(
    "/{campaign_id}/scenes",
    response_model=CampaignSceneResponse,
)
def create_campaign_scene_endpoint(
    campaign_id: int,
    payload: CampaignSceneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_campaign_scene(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        image_url=payload.image_url,
    )


@router.get(
    "/{campaign_id}/scenes",
    response_model=list[CampaignSceneResponse],
)
def get_campaign_scenes_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaign_scenes(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.get(
    "/{campaign_id}/current-scene",
    response_model=CampaignSceneResponse | None,
)
def get_current_campaign_scene_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_current_campaign_scene(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.patch(
    "/{campaign_id}/scenes/{scene_id}/activate",
    response_model=CampaignSceneResponse,
)
def activate_campaign_scene_endpoint(
    campaign_id: int,
    scene_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return activate_campaign_scene(
        db=db,
        campaign_id=campaign_id,
        scene_id=scene_id,
        user_id=user.id,
    )


@router.post(
    "/{campaign_id}/monsters",
    response_model=CampaignMonsterResponse,
)
def add_campaign_monster(
    campaign_id: int,
    payload: CampaignMonsterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign_monster = add_monster_to_campaign(
        db=db,
        campaign_id=campaign_id,
        dm_id=user.id,
        monster_id=payload.monster_id,
        quantity=payload.quantity,
    )

    broadcast_campaign_event(
        db=db,
        campaign_id=campaign_id,
        event_type="monster_added",
        data={"monster_id": campaign_monster.monster_id},
    )

    return campaign_monster


@router.get(
    "/{campaign_id}/monsters",
    response_model=list[CampaignMonsterResponse],
)
def get_campaign_monsters_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaign_monsters(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.post(
    "/{campaign_id}/items/request",
    response_model=ItemTransferRequestResponse,
)
def request_item(
    campaign_id: int,
    payload: ItemTransferRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_item_request_service(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        data=payload,
    )


@router.get(
    "/{campaign_id}/item-requests",
    response_model=list[ItemTransferRequestResponse],
)
def get_item_requests(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_item_requests_for_campaign_service(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.post(
    "/{campaign_id}/events",
    response_model=CampaignEventResponse,
)
def create_campaign_event(
    campaign_id: int,
    payload: CampaignSystemEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.dm_id == user.id).first()
    if campaign is None:
        campaign_exists = db.query(Campaign.id).filter(Campaign.id == campaign_id).first()
        if campaign_exists is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        raise HTTPException(status_code=403, detail="Only campaign DM can send events")

    event = broadcast_campaign_event(
        db=db,
        campaign_id=campaign_id,
        event_type=payload.type,
        data={"text": payload.text},
    )

    return event


@router.get(
    "/{campaign_id}/events",
    response_model=list[CampaignEventResponse],
)
def get_campaign_events_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_campaign_events(
        db=db,
        campaign_id=campaign_id,
        user_id=user.id,
        role=user.role,
    )


@router.patch(
    "/{campaign_id}/characters/{character_id}/hp",
    response_model=CharacterResponse,
)
def update_campaign_character_hp(
    campaign_id: int,
    character_id: int,
    payload: CharacterHpUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    character = update_character_hp(
        db=db,
        campaign_id=campaign_id,
        character_id=character_id,
        dm_id=user.id,
        hp=payload.hp,
    )

    broadcast_campaign_event(
        db=db,
        campaign_id=campaign_id,
        event_type="hp_updated",
        data={"character_id": character.id, "hp": character.current_hp},
    )

    return character
