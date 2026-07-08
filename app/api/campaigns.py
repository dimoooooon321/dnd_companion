from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse
)

from app.api.dependencies import get_current_user
from app.models.campaign import Campaign


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)



@router.post(
    "/",
    response_model=CampaignResponse
)
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    new_campaign = Campaign(
        name=campaign.name,
        description=campaign.description,
        dm_id=user.id
    )


    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)


    return new_campaign