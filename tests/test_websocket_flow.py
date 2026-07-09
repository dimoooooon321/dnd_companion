import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
import sys


temp_db = tempfile.NamedTemporaryFile(prefix="dnd_ws_", suffix=".sqlite3", delete=False)
temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
from app.models import *  # noqa: F401,F403


client = TestClient(app)


class WebSocketFlowTests(unittest.TestCase):
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

    def test_campaign_websocket_access_and_broadcast(self) -> None:
        suffix = uuid4().hex[:8]
        dm_email = f"ws-dm-{suffix}@example.com"
        player_email = f"ws-player-{suffix}@example.com"
        outsider_email = f"ws-outsider-{suffix}@example.com"

        dm_token, dm_id = self._register_and_login(dm_email, "dm")
        player_token, _ = self._register_and_login(player_email, "player")
        outsider_token, _ = self._register_and_login(outsider_email, "player")

        dm_headers = {"Authorization": f"Bearer {dm_token}"}
        player_headers = {"Authorization": f"Bearer {player_token}"}

        campaign_create = client.post(
            "/campaigns/",
            json={"name": f"WebSocket Forge {suffix}", "description": "WS test"},
            headers=dm_headers,
        )
        self.assertEqual(campaign_create.status_code, 200, campaign_create.text)
        campaign_id = campaign_create.json()["id"]

        character_create = client.post(
            "/characters/",
            json={
                "name": "Liora",
                "race": "Elf",
                "class_name": "Wizard",
                "max_hp": 12,
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

        with client.websocket_connect(f"/ws/campaigns/{campaign_id}?token={dm_token}") as dm_ws:
            with client.websocket_connect(
                f"/ws/campaigns/{campaign_id}?token={player_token}"
            ) as player_ws:
                dm_ws.send_json({"type": "message", "data": "hello"})

                dm_message = dm_ws.receive_json()
                player_message = player_ws.receive_json()

                self.assertEqual(dm_message["type"], "message")
                self.assertEqual(dm_message["from"], dm_id)
                self.assertEqual(dm_message["data"], "hello")

                self.assertEqual(player_message["type"], "message")
                self.assertEqual(player_message["data"], "hello")
                self.assertEqual(player_message["from"], dm_message["from"])

        with self.assertRaises(Exception):
            with client.websocket_connect(
                f"/ws/campaigns/{campaign_id}?token={outsider_token}"
            ):
                pass


if __name__ == "__main__":
    unittest.main()
