from __future__ import annotations

import asyncio

import anyio
from sqlalchemy.orm import Session

from app.models.campaign_event import CampaignEvent
from app.services.campaign_service import get_campaign_for_user
from app.websocket.manager import manager
from app.websocket.schemas import WebSocketEvent


def _build_websocket_message(event_type: str, data: dict[str, object]) -> dict[str, object]:
    event = WebSocketEvent(type=event_type, data=data)
    message = event.model_dump()
    return message


def create_campaign_event(
    db: Session,
    campaign_id: int,
    event_type: str,
    data: dict[str, object],
) -> CampaignEvent:
    event = CampaignEvent(
        campaign_id=campaign_id,
        type=event_type,
        data=data,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_campaign_events(
    db: Session,
    campaign_id: int,
    user_id: int,
    role: str,
) -> list[CampaignEvent]:
    get_campaign_for_user(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id,
        role=role,
    )

    return (
        db.query(CampaignEvent)
        .filter(CampaignEvent.campaign_id == campaign_id)
        .order_by(CampaignEvent.id)
        .all()
    )


def broadcast_campaign_event(
    db: Session,
    campaign_id: int,
    event_type: str,
    data: dict[str, object],
) -> CampaignEvent:
    event = create_campaign_event(
        db=db,
        campaign_id=campaign_id,
        event_type=event_type,
        data=data,
    )

    message = _build_websocket_message(event_type, data)

    try:
        anyio.from_thread.run(manager.broadcast, campaign_id, message)
    except RuntimeError:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(manager.broadcast(campaign_id, message))
        else:
            loop.create_task(manager.broadcast(campaign_id, message))

    return event
