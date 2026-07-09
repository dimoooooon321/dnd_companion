from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item
from app.models.item_request import ItemTransferRequest


def create_item_request(
    db: Session,
    campaign_id: int,
    user_id: int,
    data,
):
    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()

    if payload["quantity"] < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    character = (
        db.query(Character)
        .filter(Character.id == payload["character_id"], Character.owner_id == user_id)
        .first()
    )
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    membership = (
        db.query(CampaignMembership.id)
        .filter(
            CampaignMembership.campaign_id == campaign_id,
            CampaignMembership.character_id == character.id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="Character must be a member of the campaign",
        )

    item = db.query(Item).filter(Item.id == payload["item_id"]).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    request = ItemTransferRequest(
        campaign_id=campaign_id,
        character_id=character.id,
        item_id=item.id,
        quantity=payload["quantity"],
        status="pending",
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_item_requests_for_campaign(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
):
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.dm_id == user_id)
        .first()
    )

    if campaign is None:
        campaign_exists = db.query(Campaign.id).filter(Campaign.id == campaign_id).first()
        if campaign_exists is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        raise HTTPException(status_code=403, detail="Only campaign DM can view item requests")

    return (
        db.query(ItemTransferRequest)
        .filter(ItemTransferRequest.campaign_id == campaign_id)
        .order_by(ItemTransferRequest.id)
        .all()
    )


def _get_pending_request(db: Session, request_id: int) -> ItemTransferRequest:
    request = db.query(ItemTransferRequest).filter(ItemTransferRequest.id == request_id).first()

    if request is None:
        raise HTTPException(status_code=404, detail="Item request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Item request already processed")

    return request


def _ensure_dm_can_process(db: Session, request: ItemTransferRequest, user_id: int) -> None:
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == request.campaign_id, Campaign.dm_id == user_id)
        .first()
    )

    if campaign is None:
        campaign_exists = db.query(Campaign.id).filter(Campaign.id == request.campaign_id).first()
        if campaign_exists is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        raise HTTPException(status_code=403, detail="Only campaign DM can process item requests")


def approve_item_request(db: Session, request_id: int, user_id: int):
    request = _get_pending_request(db, request_id)
    _ensure_dm_can_process(db, request, user_id)

    inventory_item = (
        db.query(CharacterItem)
        .filter(
            CharacterItem.character_id == request.character_id,
            CharacterItem.item_id == request.item_id,
        )
        .first()
    )

    if inventory_item is None:
        inventory_item = CharacterItem(
            character_id=request.character_id,
            item_id=request.item_id,
            quantity=request.quantity,
        )
        db.add(inventory_item)
    else:
        inventory_item.quantity += request.quantity

    request.status = "approved"
    request.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    return request


def reject_item_request(db: Session, request_id: int, user_id: int):
    request = _get_pending_request(db, request_id)
    _ensure_dm_can_process(db, request, user_id)

    request.status = "rejected"
    request.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    return request
