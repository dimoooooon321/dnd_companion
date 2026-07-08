from sqlalchemy.orm import Session

from app.models.campaign import Campaign


def create_campaign(
    db: Session,
    user_id: int,
    name: str,
    description: str | None = None,
):
    campaign = Campaign(
        name=name,
        description=description,
        dm_id=user_id,
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return campaign
