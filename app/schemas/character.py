from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    race: str
    class_name: str
    max_hp: int
    current_hp: int | None = None

    level: int = 1
    experience: int = 0

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10


class CharacterHpUpdate(BaseModel):
    hp: int


class CharacterResponse(BaseModel):
    id: int
    name: str
    race: str
    class_name: str
    level: int
    experience: int
    max_hp: int
    current_hp: int

    class Config:
        from_attributes = True
