from __future__ import annotations

from fastapi import HTTPException, WebSocket
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.campaign import Campaign
from app.models.campaign_membership import CampaignMembership
from app.models.character import Character
from app.models.user import User
from app.services.user_service import get_user_by_id


def get_websocket_token(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return token

    authorization = websocket.headers.get("authorization")
    if not authorization:
        return None

    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()

    return authorization.strip() or None


def get_user_from_token(db: Session, token: str) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id_int = int(user_id)
    except (JWTError, TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = get_user_by_id(db, user_id_int)
    if user is None:
        raise credentials_exception

    return user


def get_campaign_or_404(db: Session, campaign_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def user_has_campaign_access(db: Session, campaign: Campaign, user: User) -> bool:
    if user.role == "dm" and campaign.dm_id == user.id:
        return True

    return (
        db.query(CampaignMembership.id)
        .join(Character, Character.id == CampaignMembership.character_id)
        .filter(
            CampaignMembership.campaign_id == campaign.id,
            Character.owner_id == user.id,
        )
        .first()
        is not None
    )


def authorize_websocket_campaign_access(
    db: Session,
    campaign_id: int,
    token: str,
) -> tuple[User, Campaign]:
    user = get_user_from_token(db, token)
    campaign = get_campaign_or_404(db, campaign_id)

    if not user_has_campaign_access(db, campaign, user):
        raise HTTPException(status_code=403, detail="You do not have access to this campaign")

    return user, campaign


def build_message_event(user_id: int, data: str | None) -> dict:
    return {
        "type": "message",
        "from": user_id,
        "data": data,
    }
