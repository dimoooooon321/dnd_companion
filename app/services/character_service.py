from sqlalchemy.orm import Session

from app.models.character import Character


def create_character(
    db: Session,
    owner_id: int,
    data
):

    character = Character(
        owner_id=owner_id,

        name=data.name,
        race=data.race,
        class_name=data.class_name,

        level=data.level,
        experience=data.experience,

        max_hp=data.max_hp,
        current_hp=data.current_hp,

        strength=data.strength,
        dexterity=data.dexterity,
        constitution=data.constitution,
        intelligence=data.intelligence,
        wisdom=data.wisdom,
        charisma=data.charisma
    )


    db.add(character)
    db.commit()
    db.refresh(character)

    return character