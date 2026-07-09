from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.campaign_monster import CampaignMonster
from app.models.character import Character
from app.models.monster import Monster
from app.models.user import User


def create_monster(
    db: Session,
    created_by: int,
    data,
):
    user = db.query(User).filter(User.id == created_by).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "dm":
        raise HTTPException(status_code=403, detail="Only DM can create monsters")

    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()

    monster = Monster(
        created_by=created_by,
        name=payload["name"],
        description=payload["description"],
        hp=payload["hp"],
        armor_class=payload["armor_class"],
        challenge_rating=payload["challenge_rating"],
        image_url=payload.get("image_url"),
    )

    db.add(monster)
    db.commit()
    db.refresh(monster)

    return monster


def get_monsters(
    db: Session,
    user_id: int,
    role: str,
):
    query = db.query(Monster)

    if role == "dm":
        return query.filter(Monster.created_by == user_id).order_by(Monster.id).all()

    return (
        query.join(CampaignMonster, CampaignMonster.monster_id == Monster.id)
        .join(Campaign, Campaign.id == CampaignMonster.campaign_id)
        .join(CampaignMembership, CampaignMembership.campaign_id == Campaign.id)
        .join(Character, Character.id == CampaignMembership.character_id)
        .filter(Character.owner_id == user_id)
        .order_by(Monster.id)
        .distinct()
        .all()
    )


def get_monster(
    db: Session,
    monster_id: int,
    user_id: int,
    role: str,
):
    monster = db.query(Monster).filter(Monster.id == monster_id).first()

    if monster is None:
        raise HTTPException(status_code=404, detail="Monster not found")

    if role == "dm":
        if monster.created_by != user_id:
            raise HTTPException(status_code=403, detail="You do not have access to this monster")

        return monster

    has_access = (
        db.query(CampaignMonster.id)
        .join(Campaign, Campaign.id == CampaignMonster.campaign_id)
        .join(CampaignMembership, CampaignMembership.campaign_id == Campaign.id)
        .join(Character, Character.id == CampaignMembership.character_id)
        .filter(
            CampaignMonster.monster_id == monster_id,
            Character.owner_id == user_id,
        )
        .first()
        is not None
    )

    if not has_access:
        raise HTTPException(status_code=403, detail="You do not have access to this monster")

    return monster


def delete_monster(
    db: Session,
    monster_id: int,
    user_id: int,
):
    monster = db.query(Monster).filter(Monster.id == monster_id).first()

    if monster is None:
        raise HTTPException(status_code=404, detail="Monster not found")

    if monster.created_by != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own monsters")

    db.delete(monster)
    db.commit()
