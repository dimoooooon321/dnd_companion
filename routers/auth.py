# app/routers/auth.py
from fastapi import APIRouter, Request, Response, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User, Campaign, Character
from app.auth import (
    hash_password, verify_password, create_access_token,
    set_auth_cookie, clear_auth_cookie, get_current_user,
    generate_room_code, get_current_room
)

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="app/templates")


# ==================== ГЛАВНАЯ ====================
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==================== ДМ: РЕГИСТРАЦИЯ / ЛОГИН ====================
@router.get("/dm/register", response_class=HTMLResponse)
async def dm_register_page(request: Request):
    return templates.TemplateResponse("auth/dm_register.html", {"request": request})

@router.post("/dm/register")
async def dm_register(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    # Проверяем, нет ли такого email
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    user = User(email=email, hashed_password=hash_password(password), is_dm=True)
    session.add(user)
    await session.commit()
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return RedirectResponse(url="/dm/dashboard", status_code=303)


@router.get("/dm/login", response_class=HTMLResponse)
async def dm_login_page(request: Request):
    return templates.TemplateResponse("auth/dm_login.html", {"request": request})

@router.post("/dm/login")
async def dm_login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_dm:
        raise HTTPException(status_code=403, detail="Это не аккаунт Мастера")
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return RedirectResponse(url="/dm/dashboard", status_code=303)


@router.get("/dm/logout")
async def dm_logout(response: Response):
    clear_auth_cookie(response)
    return RedirectResponse(url="/", status_code=303)


# ==================== ИГРОК: РЕГИСТРАЦИЯ / ЛОГИН ====================
@router.get("/player/register", response_class=HTMLResponse)
async def player_register_page(request: Request):
    return templates.TemplateResponse("auth/player_register.html", {"request": request})

@router.post("/player/register")
async def player_register(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    user = User(email=email, hashed_password=hash_password(password), is_dm=False)
    session.add(user)
    await session.commit()
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return RedirectResponse(url="/player/dashboard", status_code=303)


@router.get("/player/login", response_class=HTMLResponse)
async def player_login_page(request: Request):
    return templates.TemplateResponse("auth/player_login.html", {"request": request})

@router.post("/player/login")
async def player_login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if user.is_dm:
        raise HTTPException(status_code=403, detail="Это аккаунт Мастера")
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return RedirectResponse(url="/player/dashboard", status_code=303)


# ==================== ДАШБОРД ИГРОКА (выбор персонажа) ====================
@router.get("/player/dashboard", response_class=HTMLResponse)
async def player_dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Получаем всех персонажей этого игрока
    result = await session.execute(
        select(Character).where(Character.owner_id == user.id)
    )
    characters = result.scalars().all()
    return templates.TemplateResponse(
        "player/dashboard.html",
        {"request": request, "user": user, "characters": characters}
    )


# ==================== ОБЩИЙ ЭКРАН (ТВ): вход по PIN-коду ====================
@router.get("/table/join", response_class=HTMLResponse)
async def table_join_page(request: Request):
    return templates.TemplateResponse("table/join.html", {"request": request})

@router.post("/table/join")
async def table_join(
    response: Response,
    room_code: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    # Проверяем, что такая кампания существует
    result = await session.execute(
        select(Campaign).where(Campaign.room_code == room_code)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Комната не найдена. Проверьте код.")
    
    # Сохраняем код комнаты в cookie (не JWT — это просто "устройство")
    response.set_cookie(
        key="room_code",
        value=room_code,
        httponly=False,  # Нужно будет читать JS для WebSocket
        max_age=60 * 60 * 8,  # 8 часов
        samesite="lax",
    )
    return RedirectResponse(url=f"/table/view/{room_code}", status_code=303)


@router.get("/table/logout")
async def table_logout(response: Response):
    response.delete_cookie("room_code")
    return RedirectResponse(url="/table/join", status_code=303)