from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.character import CharacterCreate, CharacterResponse
from app.services.character_service import (
    create_character,
    get_character_by_id,
    get_user_characters,
    update_character,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("/", response_model=CharacterResponse)
def create(
    data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_character(db, owner_id=current_user.id, data=data)


@router.get("/", response_model=list[CharacterResponse])
def list_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_characters(db, current_user.id)


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    character = get_character_by_id(db, character_id)
    if character is None or character.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/{character_id}", response_model=CharacterResponse)
def update_character_route(
    character_id: int,
    data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    character = update_character(db, character_id, current_user.id, data)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character