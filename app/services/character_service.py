from sqlalchemy.orm import Session

from app.models.character import Character


def create_character(db: Session, owner_id: int, data):
    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()

    character = Character(
        owner_id=owner_id,
        name=payload["name"],
        race=payload["race"],
        class_name=payload["class_name"],
        level=payload.get("level", 1),
        experience=payload.get("experience", 0),
        max_hp=payload["max_hp"],
        current_hp=payload.get("current_hp") if payload.get("current_hp") is not None else payload["max_hp"],
        strength=payload.get("strength", 10),
        dexterity=payload.get("dexterity", 10),
        constitution=payload.get("constitution", 10),
        intelligence=payload.get("intelligence", 10),
        wisdom=payload.get("wisdom", 10),
        charisma=payload.get("charisma", 10),
    )

    db.add(character)
    db.commit()
    db.refresh(character)

    return character


def get_character_by_id(db: Session, character_id: int):
    return db.query(Character).filter(Character.id == character_id).first()


def get_user_characters(db: Session, owner_id: int):
    return db.query(Character).filter(Character.owner_id == owner_id).order_by(Character.id).all()


def update_character(db: Session, character_id: int, owner_id: int, data):
    character = (
        db.query(Character)
        .filter(Character.id == character_id, Character.owner_id == owner_id)
        .first()
    )

    if character is None:
        return None

    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()

    for field in [
        "name",
        "race",
        "class_name",
        "level",
        "experience",
        "max_hp",
        "current_hp",
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ]:
        if field in payload and payload[field] is not None:
            setattr(character, field, payload[field])

    if "max_hp" in payload and payload["max_hp"] is not None and payload.get("current_hp") is None:
        character.current_hp = payload["max_hp"]

    db.commit()
    db.refresh(character)

    return character