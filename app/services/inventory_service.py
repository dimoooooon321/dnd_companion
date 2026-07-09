from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item


def get_character_inventory(
    db: Session,
    character_id: int,
    user_id: int,
    role: str,
):
    character = db.query(Character).filter(Character.id == character_id).first()

    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.owner_id != user_id and role != "dm":
        raise HTTPException(status_code=403, detail="You do not have access to this inventory")

    if character.owner_id != user_id:
        dm_has_access = (
            db.query(CampaignMembership.id)
            .join(Campaign, Campaign.id == CampaignMembership.campaign_id)
            .filter(
                CampaignMembership.character_id == character_id,
                Campaign.dm_id == user_id,
            )
            .first()
            is not None
        )

        if not dm_has_access:
            raise HTTPException(status_code=403, detail="You do not have access to this inventory")

    return (
        db.query(CharacterItem)
        .options(joinedload(CharacterItem.item))
        .join(Item, Item.id == CharacterItem.item_id)
        .filter(CharacterItem.character_id == character_id)
        .order_by(CharacterItem.id)
        .all()
    )
