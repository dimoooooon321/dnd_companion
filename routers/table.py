# app/routers/table.py
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from app.ws_manager import manager

router = APIRouter(prefix="/table", tags=["Table"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/join")
async def table_join_page(request: Request):
    # Страница ввода 6-значного кода комнаты
    return templates.TemplateResponse("table/join.html", {"request": request})

@router.get("/view/{room_code}")
async def table_view(request: Request, room_code: str):
    # Сам экран для ТВ. Рендерится шаблон, который по WS слушает ДМа
    return templates.TemplateResponse("table/view.html", {"request": request, "room_code": room_code})

@router.websocket("/ws/{room_code}")
async def table_websocket(websocket: WebSocket, room_code: str):
    await manager.connect(websocket, room_code, role="table")
    try:
        while True:
            # Общий экран только слушает, но может отправлять пинги
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(room_code, role="table")