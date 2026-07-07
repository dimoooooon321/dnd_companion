# app/routers/player.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/player", tags=["Player"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/character/{character_id}")
async def player_character_sheet(request: Request, character_id: int):
    # Здесь будет проверка, что юзер авторизован и это ЕГО персонаж
    return templates.TemplateResponse("player/sheet.html", {"request": request, "char_id": character_id})