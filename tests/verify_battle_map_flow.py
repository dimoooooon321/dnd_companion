import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)

suffix = uuid4().hex[:8]
dm_email = f"battle-dm-{suffix}@example.com"
player_email = f"battle-player-{suffix}@example.com"
other_email = f"battle-other-{suffix}@example.com"
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

other_register = client.post(
    "/auth/register",
    json={"email": other_email, "password": password, "role": "player"},
)
assert other_register.status_code == 200, other_register.json()

other_login = client.post(
    "/auth/login",
    data={"username": other_email, "password": password},
)
assert other_login.status_code == 200, other_login.json()
other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

character_create = client.post(
    "/characters/",
    json={
        "name": "Aldric",
        "race": "Human",
        "class_name": "Fighter",
        "max_hp": 18,
    },
    headers=player_headers,
)
assert character_create.status_code == 200, character_create.json()
character_id = character_create.json()["id"]

monster_create = client.post(
    "/monsters/",
    json={
        "name": "Goblin",
        "description": "A small goblin",
        "hp": 8,
        "armor_class": 13,
        "challenge_rating": 0.25,
    },
    headers=dm_headers,
)
assert monster_create.status_code == 200, monster_create.json()
monster_id = monster_create.json()["id"]

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"Battle Campaign {suffix}", "description": "Battle map test"},
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

campaign_monster_add = client.post(
    f"/campaigns/{campaign_id}/monsters",
    json={"monster_id": monster_id, "quantity": 1},
    headers=dm_headers,
)
assert campaign_monster_add.status_code == 200, campaign_monster_add.json()

map_create = client.post(
    f"/campaigns/{campaign_id}/battle-maps",
    json={"name": "Arena", "width": 10, "height": 8},
    headers=dm_headers,
)
assert map_create.status_code == 200, map_create.json()
map_id = map_create.json()["id"]

character_token = client.post(
    f"/battle-maps/{map_id}/tokens",
    json={"token_type": "character", "character_id": character_id, "x": 3, "y": 4},
    headers=dm_headers,
)
assert character_token.status_code == 200, character_token.json()

monster_token = client.post(
    f"/battle-maps/{map_id}/tokens",
    json={"token_type": "monster", "monster_id": monster_id, "x": 8, "y": 6},
    headers=dm_headers,
)
assert monster_token.status_code == 200, monster_token.json()

player_maps = client.get(f"/campaigns/{campaign_id}/battle-maps", headers=player_headers)
assert player_maps.status_code == 200, player_maps.json()
assert len(player_maps.json()) == 1

player_map_detail = client.get(f"/battle-maps/{map_id}", headers=player_headers)
assert player_map_detail.status_code == 200, player_map_detail.json()
assert player_map_detail.json()["id"] == map_id

player_tokens = client.get(f"/battle-maps/{map_id}/tokens", headers=player_headers)
assert player_tokens.status_code == 200, player_tokens.json()
assert len(player_tokens.json()) == 2

player_create_map = client.post(
    f"/campaigns/{campaign_id}/battle-maps",
    json={"name": "Forbidden", "width": 5, "height": 5},
    headers=player_headers,
)
assert player_create_map.status_code == 403, player_create_map.json()

other_map = client.get(f"/battle-maps/{map_id}", headers=other_headers)
assert other_map.status_code == 403, other_map.json()

print("battle_map_flow_ok")
