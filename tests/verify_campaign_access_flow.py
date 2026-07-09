import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)

suffix = uuid4().hex[:8]
dm_email = f"campaign-access-dm-{suffix}@example.com"
player_email = f"campaign-access-player-{suffix}@example.com"
password = "strongpass123"


dm_register = client.post(
    "/auth/register",
    json={"email": dm_email, "password": password, "role": "dm"},
)
assert dm_register.status_code == 200, dm_register.json()

dm_login = client.post(
    "/auth/login",
    data={"username": dm_email, "password": password},
)
assert dm_login.status_code == 200, dm_login.json()
dm_headers = {"Authorization": f"Bearer {dm_login.json()['access_token']}"}

player_register = client.post(
    "/auth/register",
    json={"email": player_email, "password": password, "role": "player"},
)
assert player_register.status_code == 200, player_register.json()

player_login = client.post(
    "/auth/login",
    data={"username": player_email, "password": password},
)
assert player_login.status_code == 200, player_login.json()
player_headers = {"Authorization": f"Bearer {player_login.json()['access_token']}"}

character_create = client.post(
    "/characters/",
    json={
        "name": "Astra",
        "race": "Elf",
        "class_name": "Wizard",
        "max_hp": 12,
    },
    headers=player_headers,
)
assert character_create.status_code == 200, character_create.json()
character_id = character_create.json()["id"]

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"Campaign {suffix}", "description": "Access test"},
    headers=dm_headers,
)
assert campaign_create.status_code == 200, campaign_create.json()
campaign_id = campaign_create.json()["id"]

membership_create = client.post(
    f"/campaigns/{campaign_id}/members",
    json={"character_id": character_id},
    headers=dm_headers,
)
assert membership_create.status_code == 200, membership_create.json()

dm_campaigns = client.get("/campaigns/", headers=dm_headers)
assert dm_campaigns.status_code == 200, dm_campaigns.json()
dm_campaign_ids = {item["id"] for item in dm_campaigns.json()}
assert campaign_id in dm_campaign_ids

player_campaigns = client.get("/campaigns/", headers=player_headers)
assert player_campaigns.status_code == 200, player_campaigns.json()
player_campaign_ids = {item["id"] for item in player_campaigns.json()}
assert campaign_id in player_campaign_ids

dm_campaign = client.get(f"/campaigns/{campaign_id}", headers=dm_headers)
assert dm_campaign.status_code == 200, dm_campaign.json()
assert dm_campaign.json()["id"] == campaign_id

player_campaign = client.get(f"/campaigns/{campaign_id}", headers=player_headers)
assert player_campaign.status_code == 200, player_campaign.json()
assert player_campaign.json()["id"] == campaign_id

print("dm_campaigns", dm_campaigns.json())
print("player_campaigns", player_campaigns.json())
print("dm_campaign", dm_campaign.json())
print("player_campaign", player_campaign.json())
