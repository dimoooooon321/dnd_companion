import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)
suffix = uuid4().hex[:8]

dm_email = f"campaign-dm-{suffix}@example.com"
player_email = f"campaign-player-{suffix}@example.com"
password = "strongpass123"


dm_register = client.post(
    "/auth/register",
    json={"email": dm_email, "password": password, "role": "dm"},
)
print("dm_register", dm_register.status_code, dm_register.json())

dm_login = client.post(
    "/auth/login",
    data={"username": dm_email, "password": password},
)
print("dm_login", dm_login.status_code, dm_login.json())

dm_headers = {"Authorization": f"Bearer {dm_login.json()['access_token']}"}

player_register = client.post(
    "/auth/register",
    json={"email": player_email, "password": password, "role": "player"},
)
print("player_register", player_register.status_code, player_register.json())

player_login = client.post(
    "/auth/login",
    data={"username": player_email, "password": password},
)
print("player_login", player_login.status_code, player_login.json())

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
print("character_create", character_create.status_code, character_create.json())

character_id = character_create.json()["id"]

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"Campaign {suffix}", "description": "Membership test"},
    headers=dm_headers,
)
print("campaign_create", campaign_create.status_code, campaign_create.json())

campaign_id = campaign_create.json()["id"]

membership_create = client.post(
    f"/campaigns/{campaign_id}/members",
    json={"character_id": character_id},
    headers=dm_headers,
)
print("membership_create", membership_create.status_code, membership_create.json())

members_get = client.get(
    f"/campaigns/{campaign_id}/members",
    headers=dm_headers,
)
print("members_get", members_get.status_code, members_get.json())
