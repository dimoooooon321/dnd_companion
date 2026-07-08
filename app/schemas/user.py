from pydantic import BaseModel


class UserCreate(BaseModel):

    email: str
    password: str
    role: str = "player"


class UserLogin(BaseModel):

    email: str
    password: str



class UserResponse(BaseModel):

    id: int
    email: str
    role: str

    class Config:
        from_attributes = True