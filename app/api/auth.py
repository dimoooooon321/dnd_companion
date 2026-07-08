from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_current_user
from app.models.user import User
from fastapi import Depends

from app.core.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin
)

from app.services.auth_service import (
    create_user,
    authenticate_user
)

from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)



@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = create_user(
        db,
        user.email,
        user.password,
        user.role
    )


    return {
        "id": new_user.id,
        "email": new_user.email
    }



@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )


    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )


    token = create_access_token(
        {
            "sub": str(db_user.id),
            "role": db_user.role
        }
    )


    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }