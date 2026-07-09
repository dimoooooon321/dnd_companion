from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from starlette.responses import JSONResponse

from app.core.database import SessionLocal
from app.websocket.events import (
    authorize_websocket_campaign_access,
    build_message_event,
    get_websocket_token,
)
from app.websocket.manager import manager


router = APIRouter(tags=["WebSocket"])


async def deny_websocket(websocket: WebSocket, status_code: int, detail: str) -> None:
    try:
        await websocket.send_denial_response(
            JSONResponse(
                {"detail": detail},
                status_code=status_code,
            )
        )
    except RuntimeError:
        await websocket.close(code=1008)


@router.websocket("/ws/campaigns/{campaign_id}")
async def campaign_websocket(
    websocket: WebSocket,
    campaign_id: int,
    token: str | None = Query(default=None),
) -> None:
    db = SessionLocal()
    try:
        resolved_token = token or get_websocket_token(websocket)
        if resolved_token is None:
            await deny_websocket(websocket, 401, "Could not validate credentials")
            return

        try:
            user, campaign = authorize_websocket_campaign_access(
                db=db,
                campaign_id=campaign_id,
                token=resolved_token,
            )
        except HTTPException as exc:
            await deny_websocket(websocket, exc.status_code, exc.detail)
            return

        await manager.connect(campaign.id, websocket)

        try:
            while True:
                payload = await websocket.receive_json()
                if payload.get("type") == "message":
                    await manager.broadcast(
                        campaign.id,
                        build_message_event(user.id, payload.get("data")),
                    )
        except WebSocketDisconnect:
            pass
        finally:
            manager.disconnect(campaign.id, websocket)
    finally:
        db.close()
