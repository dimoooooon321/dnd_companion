from pydantic import BaseModel


class CampaignMembershipCreate(BaseModel):
    character_id: int
