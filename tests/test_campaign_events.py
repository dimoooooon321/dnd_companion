import os
import sys
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4


temp_db = tempfile.NamedTemporaryFile(prefix="dnd_events_", suffix=".sqlite3", delete=False)
temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
from app.websocket.manager import manager
from app.models import *  # noqa: F401,F403


client = TestClient(app)


class CampaignEventTests(unittest.TestCase):
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

    def _register_and_login(self, email: str, role: str) -> tuple[str, int]:
        register = client.post(
            "/auth/register",
            json={"email": email, "password": "strongpass123", "role": role},
        )
        self.assertEqual(register.status_code, 200, register.text)

        login = client.post(
            "/auth/login",
            data={"username": email, "password": "strongpass123"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        return login.json()["access_token"], register.json()["id"]

    def test_campaign_events_broadcast_to_connected_players(self) -> None:
        suffix = uuid4().hex[:8]
        dm_token, _ = self._register_and_login(f"events-dm-{suffix}@example.com", "dm")
        player_token, _ = self._register_and_login(f"events-player-{suffix}@example.com", "player")

        dm_headers = {"Authorization": f"Bearer {dm_token}"}
        player_headers = {"Authorization": f"Bearer {player_token}"}

        campaign_create = client.post(
            "/campaigns/",
            json={"name": f"Events Forge {suffix}", "description": "Event test"},
            headers=dm_headers,
        )
        self.assertEqual(campaign_create.status_code, 200, campaign_create.text)
        campaign_id = campaign_create.json()["id"]

        character_create = client.post(
            "/characters/",
            json={
                "name": "Mira",
                "race": "Human",
                "class_name": "Cleric",
                "max_hp": 20,
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

        monster_create = client.post(
            "/monsters/",
            json={
                "name": "Goblin",
                "description": "Small and annoying.",
                "hp": 7,
                "armor_class": 12,
                "challenge_rating": 0.25,
            },
            headers=dm_headers,
        )
        self.assertEqual(monster_create.status_code, 200, monster_create.text)
        monster_id = monster_create.json()["id"]

        with client.websocket_connect(f"/ws/campaigns/{campaign_id}?token={dm_token}") as dm_ws:
            with client.websocket_connect(
                f"/ws/campaigns/{campaign_id}?token={player_token}"
            ) as player_ws:
                self.assertEqual(len(manager.get_connections(campaign_id)), 2)

                add_campaign_monster = client.post(
                    f"/campaigns/{campaign_id}/monsters",
                    json={"monster_id": monster_id, "quantity": 1},
                    headers=dm_headers,
                )
                self.assertEqual(add_campaign_monster.status_code, 200, add_campaign_monster.text)

                player_monster_event = player_ws.receive_json()
                self.assertEqual(player_monster_event, {"type": "monster_added", "data": {"monster_id": monster_id}})

                hp_update = client.patch(
                    f"/campaigns/{campaign_id}/characters/{character_id}/hp",
                    json={"hp": 15},
                    headers=dm_headers,
                )
                self.assertEqual(hp_update.status_code, 200, hp_update.text)

                player_hp_event = player_ws.receive_json()
                self.assertEqual(
                    player_hp_event,
                    {"type": "hp_updated", "data": {"character_id": character_id, "hp": 15}},
                )

                dm_ws.receive_json()
                dm_ws.receive_json()


if __name__ == "__main__":
    unittest.main()
