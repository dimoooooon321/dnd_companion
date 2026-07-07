# app/routers/dm.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/dm", tags=["DM"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def dm_dashboard(request: Request):
    # Здесь будет проверка JWT токена ДМа (в реальном коде через Depends)
    return templates.TemplateResponse("dm/dashboard.html", {"request": request, "role": "dm"})