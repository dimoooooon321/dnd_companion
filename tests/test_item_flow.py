import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
import sys


temp_db = tempfile.NamedTemporaryFile(prefix="dnd_items_", suffix=".sqlite3", delete=False)
temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
from app.models import *  # noqa: F401,F403


client = TestClient(app)


class ItemFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(bind=engine)
        client.close()
        engine.dispose()
        try:
            Path(temp_db.name).unlink(missing_ok=True)
        except TypeError:
            if Path(temp_db.name).exists():
                Path(temp_db.name).unlink()

    def test_full_item_request_flow(self) -> None:
        suffix = uuid4().hex[:8]
        dm_email = f"item-dm-{suffix}@example.com"
        player_email = f"item-player-{suffix}@example.com"
        password = "strongpass123"

        dm_register = client.post(
            "/auth/register",
            json={"email": dm_email, "password": password, "role": "dm"},
        )
        self.assertEqual(dm_register.status_code, 200, dm_register.text)

        dm_login = client.post(
            "/auth/login",
            data={"username": dm_email, "password": password},
        )
        self.assertEqual(dm_login.status_code, 200, dm_login.text)
        dm_token = dm_login.json()["access_token"]
        dm_headers = {"Authorization": f"Bearer {dm_token}"}

        item_create = client.post(
            "/items/",
            json={
                "name": "Potion of Healing",
                "description": "Restores a little vitality.",
                "item_type": "consumable",
                "weight": 0.5,
            },
            headers=dm_headers,
        )
        self.assertEqual(item_create.status_code, 200, item_create.text)
        item_id = item_create.json()["id"]

        campaign_create = client.post(
            "/campaigns/",
            json={"name": f"Forge of Echoes {suffix}", "description": "Integration test"},
            headers=dm_headers,
        )
        self.assertEqual(campaign_create.status_code, 200, campaign_create.text)
        campaign_id = campaign_create.json()["id"]

        player_register = client.post(
            "/auth/register",
            json={"email": player_email, "password": password, "role": "player"},
        )
        self.assertEqual(player_register.status_code, 200, player_register.text)

        player_login = client.post(
            "/auth/login",
            data={"username": player_email, "password": password},
        )
        self.assertEqual(player_login.status_code, 200, player_login.text)
        player_token = player_login.json()["access_token"]
        player_headers = {"Authorization": f"Bearer {player_token}"}

        character_create = client.post(
            "/characters/",
            json={
                "name": "Aria",
                "race": "Elf",
                "class_name": "Ranger",
                "max_hp": 18,
            },
            headers=player_headers,
        )
        self.assertEqual(character_create.status_code, 200, character_create.text)
        character_id = character_create.json()["id"]

        add_member = client.post(
            f"/campaigns/{campaign_id}/members",
            json={"character_id": character_id},
            headers=dm_headers,
        )
        self.assertEqual(add_member.status_code, 200, add_member.text)

        item_request = client.post(
            f"/campaigns/{campaign_id}/items/request",
            json={"character_id": character_id, "item_id": item_id, "quantity": 2},
            headers=player_headers,
        )
        self.assertEqual(item_request.status_code, 200, item_request.text)
        request_id = item_request.json()["id"]

        dm_requests = client.get(
            f"/campaigns/{campaign_id}/item-requests",
            headers=dm_headers,
        )
        self.assertEqual(dm_requests.status_code, 200, dm_requests.text)
        self.assertEqual(len(dm_requests.json()), 1)
        self.assertEqual(dm_requests.json()[0]["status"], "pending")

        approve = client.post(
            f"/item-requests/{request_id}/approve",
            headers=dm_headers,
        )
        self.assertEqual(approve.status_code, 200, approve.text)
        self.assertEqual(approve.json()["status"], "approved")

        inventory = client.get(
            f"/characters/{character_id}/inventory",
            headers=player_headers,
        )
        self.assertEqual(inventory.status_code, 200, inventory.text)
        self.assertEqual(len(inventory.json()), 1)
        self.assertEqual(inventory.json()[0]["item_id"], item_id)
        self.assertEqual(inventory.json()[0]["quantity"], 2)


if __name__ == "__main__":
    unittest.main()
