from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.character import (
    CharacterCreate,
    CharacterResponse
)

from app.services.character_service import create_character


router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)


@router.post(
    "/",
    response_model=CharacterResponse
)
def create(
    data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    character = create_character(
        db,
        owner_id=current_user.id,
        data=data
    )

    return character