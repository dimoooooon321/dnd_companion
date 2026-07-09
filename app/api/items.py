from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import (
    create_item as create_item_service,
    delete_item as delete_item_service,
    get_item_by_id as get_item_by_id_service,
    get_items as get_items_service,
)


router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemResponse)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_item_service(db=db, creator_id=user.id, data=data)


@router.get("/", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_items_service(db=db)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_item_by_id_service(db=db, item_id=item_id)


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_item_service(db=db, item_id=item_id, user_id=user.id)
    return {"detail": "Item deleted"}
