from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.item_request import ItemTransferRequestResponse
from app.services.campaign_event_service import broadcast_campaign_event
from app.services.item_request_service import (
    approve_item_request as approve_item_request_service,
    reject_item_request as reject_item_request_service,
)


router = APIRouter(tags=["Item Requests"])


@router.post("/item-requests/{request_id}/approve", response_model=ItemTransferRequestResponse)
def approve_item_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request = approve_item_request_service(db=db, request_id=request_id, user_id=user.id)

    broadcast_campaign_event(
        campaign_id=request.campaign_id,
        event_type="inventory_updated",
        data={"character_id": request.character_id},
    )

    return request


@router.post("/item-requests/{request_id}/reject", response_model=ItemTransferRequestResponse)
def reject_item_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return reject_item_request_service(db=db, request_id=request_id, user_id=user.id)
