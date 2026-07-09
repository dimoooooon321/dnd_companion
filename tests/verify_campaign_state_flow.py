import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)

suffix = uuid4().hex[:8]
dm_email = f"state-dm-{suffix}@example.com"
player_email = f"state-player-{suffix}@example.com"
outsider_email = f"state-outsider-{suffix}@example.com"
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

outsider_register = client.post(
    "/auth/register",
    json={"email": outsider_email, "password": password, "role": "player"},
)
assert outsider_register.status_code == 200, outsider_register.json()

outsider_login = client.post(
    "/auth/login",
    data={"username": outsider_email, "password": password},
)
assert outsider_login.status_code == 200, outsider_login.json()
outsider_headers = {"Authorization": f"Bearer {outsider_login.json()['access_token']}"}

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

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"State Campaign {suffix}", "description": "State test"},
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

campaign_monster_add = client.post(
    f"/campaigns/{campaign_id}/monsters",
    json={"monster_id": monster_id, "quantity": 2},
    headers=dm_headers,
)
assert campaign_monster_add.status_code == 200, campaign_monster_add.json()

scene_create = client.post(
    f"/campaigns/{campaign_id}/scenes",
    json={
        "title": f"Sanctum of Echoes {suffix}",
        "description": "A quiet chamber where the air hums with power.",
        "image_url": "https://example.com/scene.png",
    },
    headers=dm_headers,
)
assert scene_create.status_code == 200, scene_create.json()
scene_id = scene_create.json()["id"]

scene_activate = client.patch(
    f"/campaigns/{campaign_id}/scenes/{scene_id}/activate",
    headers=dm_headers,
)
assert scene_activate.status_code == 200, scene_activate.json()
assert scene_activate.json()["is_active"] is True

for index in range(12):
    event_create = client.post(
        f"/campaigns/{campaign_id}/events",
        json={"type": f"state_test_{index}", "text": f"event {index}"},
        headers=dm_headers,
    )
    assert event_create.status_code == 200, event_create.json()

dm_state = client.get(f"/campaigns/{campaign_id}/state", headers=dm_headers)
assert dm_state.status_code == 200, dm_state.json()
dm_state_data = dm_state.json()
assert dm_state_data["campaign"]["id"] == campaign_id
assert dm_state_data["current_scene"]["id"] == scene_id
assert dm_state_data["current_scene"]["is_active"] is True
assert len(dm_state_data["characters"]) == 1
assert dm_state_data["characters"][0]["id"] == character_id
assert len(dm_state_data["monsters"]) == 1
assert dm_state_data["monsters"][0]["monster"]["id"] == monster_id
assert len(dm_state_data["recent_events"]) == 10
assert dm_state_data["recent_events"][0]["type"] == "state_test_2"
assert dm_state_data["recent_events"][-1]["type"] == "state_test_11"

player_state = client.get(f"/campaigns/{campaign_id}/state", headers=player_headers)
assert player_state.status_code == 200, player_state.json()
assert player_state.json()["campaign"]["id"] == campaign_id
assert player_state.json()["current_scene"]["id"] == scene_id

outsider_state = client.get(f"/campaigns/{campaign_id}/state", headers=outsider_headers)
assert outsider_state.status_code == 403, outsider_state.json()

print("dm_state", dm_state.status_code, dm_state.json())
print("player_state", player_state.status_code, player_state.json())
print("outsider_state", outsider_state.status_code, outsider_state.json())
