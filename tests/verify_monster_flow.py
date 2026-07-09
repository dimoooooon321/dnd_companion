import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)

suffix = uuid4().hex[:8]
dm_email = f"monster-dm-{suffix}@example.com"
player_email = f"monster-player-{suffix}@example.com"
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

monster_create = client.post(
    "/monsters/",
    json={
        "name": f"Goblin Chief {suffix}",
        "description": "A sly goblin leader.",
        "hp": 18,
        "armor_class": 13,
        "challenge_rating": 1.0,
        "image_url": None,
    },
    headers=dm_headers,
)
assert monster_create.status_code == 200, monster_create.json()
monster_id = monster_create.json()["id"]

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

player_monster_create = client.post(
    "/monsters/",
    json={
        "name": f"Player Attempt {suffix}",
        "description": "This should fail.",
        "hp": 5,
        "armor_class": 10,
        "challenge_rating": 0.25,
    },
    headers=player_headers,
)
assert player_monster_create.status_code == 403, player_monster_create.json()

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"Bestiary Campaign {suffix}", "description": "Monster access test"},
    headers=dm_headers,
)
assert campaign_create.status_code == 200, campaign_create.json()
campaign_id = campaign_create.json()["id"]

campaign_monster_add = client.post(
    f"/campaigns/{campaign_id}/monsters",
    json={"monster_id": monster_id, "quantity": 2},
    headers=dm_headers,
)
assert campaign_monster_add.status_code == 200, campaign_monster_add.json()
assert campaign_monster_add.json()["monster_id"] == monster_id

character_create = client.post(
    "/characters/",
    json={
        "name": f"Astra {suffix}",
        "race": "Elf",
        "class_name": "Wizard",
        "max_hp": 12,
    },
    headers=player_headers,
)
assert character_create.status_code == 200, character_create.json()
character_id = character_create.json()["id"]

membership_add = client.post(
    f"/campaigns/{campaign_id}/members",
    json={"character_id": character_id},
    headers=dm_headers,
)
assert membership_add.status_code == 200, membership_add.json()

player_campaign_monsters = client.get(
    f"/campaigns/{campaign_id}/monsters",
    headers=player_headers,
)
assert player_campaign_monsters.status_code == 200, player_campaign_monsters.json()
assert any(item["monster_id"] == monster_id for item in player_campaign_monsters.json())

player_campaign_monster_add = client.post(
    f"/campaigns/{campaign_id}/monsters",
    json={"monster_id": monster_id, "quantity": 1},
    headers=player_headers,
)
assert player_campaign_monster_add.status_code == 403, player_campaign_monster_add.json()

print("dm_register", dm_register.status_code, dm_register.json())
print("monster_create", monster_create.status_code, monster_create.json())
print("player_monster_create", player_monster_create.status_code, player_monster_create.json())
print("campaign_create", campaign_create.status_code, campaign_create.json())
print("campaign_monster_add", campaign_monster_add.status_code, campaign_monster_add.json())
print("player_campaign_monsters", player_campaign_monsters.status_code, player_campaign_monsters.json())
print("player_campaign_monster_add", player_campaign_monster_add.status_code, player_campaign_monster_add.json())
