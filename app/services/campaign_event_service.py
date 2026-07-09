from __future__ import annotations

import asyncio

import anyio

from app.websocket.manager import manager
from app.websocket.schemas import WebSocketEvent


def broadcast_campaign_event(campaign_id: int, event_type: str, data: dict[str, object]) -> None:
    event = WebSocketEvent(type=event_type, data=data)
    message = event.model_dump()

    try:
        anyio.from_thread.run(manager.broadcast, campaign_id, message)
        return
    except RuntimeError:
        pass

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(manager.broadcast(campaign_id, message))
    else:
        loop.create_task(manager.broadcast(campaign_id, message))

