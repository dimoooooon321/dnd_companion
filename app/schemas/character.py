from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    race: str
    class_name: str

    level: int = 1
    experience: int = 0

    max_hp: int
    current_hp: int

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10



class CharacterResponse(BaseModel):
    id: int

    name: str
    race: str
    class_name: str

    level: int
    experience: int

    max_hp: int
    current_hp: int

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


    class Config:
        from_attributes = True