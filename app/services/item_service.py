from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.user import User


def create_item(
    db: Session,
    creator_id: int,
    data,
):
    user = db.query(User).filter(User.id == creator_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "dm":
        raise HTTPException(status_code=403, detail="Only DM can create items")

    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()

    item = Item(
        creator_id=creator_id,
        name=payload["name"],
        description=payload["description"],
        item_type=payload["item_type"],
        weight=payload["weight"],
        image_url=payload.get("image_url"),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_items(db: Session):
    return db.query(Item).order_by(Item.id).all()


def get_item_by_id(db: Session, item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


def delete_item(db: Session, item_id: int, user_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.creator_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own items")

    db.delete(item)
    db.commit()
