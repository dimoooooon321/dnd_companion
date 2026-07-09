from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.monster import MonsterCreate, MonsterResponse
from app.services.monster_service import (
    create_monster as create_monster_service,
    delete_monster as delete_monster_service,
    get_monster as get_monster_service,
    get_monsters as get_monsters_service,
)


router = APIRouter(prefix="/monsters", tags=["Monsters"])


@router.post("/", response_model=MonsterResponse)
def create_monster(
    data: MonsterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_monster_service(
        db=db,
        created_by=user.id,
        data=data,
    )


@router.get("/", response_model=list[MonsterResponse])
def list_monsters(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_monsters_service(
        db=db,
        user_id=user.id,
        role=user.role,
    )


@router.get("/{monster_id}", response_model=MonsterResponse)
def get_monster(
    monster_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_monster_service(
        db=db,
        monster_id=monster_id,
        user_id=user.id,
        role=user.role,
    )


@router.delete("/{monster_id}")
def delete_monster(
    monster_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_monster_service(
        db=db,
        monster_id=monster_id,
        user_id=user.id,
    )

    return {"detail": "Monster deleted"}
