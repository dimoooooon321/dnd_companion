from fastapi import Depends, HTTPException

from jose import jwt, JWTError

from sqlalchemy.orm import Session


from app.core.security import oauth2_scheme
from app.core.config import settings
from app.core.database import get_db

from app.services.user_service import get_user_by_id



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )


    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ]
        )


        user_id = payload.get("sub")


        if user_id is None:
            raise credentials_exception


    except JWTError:

        raise credentials_exception



    user = get_user_by_id(
        db,
        int(user_id)
    )


    if user is None:
        raise credentials_exception


    return user