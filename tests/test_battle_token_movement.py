import os
import sys
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4


temp_db = tempfile.NamedTemporaryFile(prefix="dnd_token_move_", suffix=".sqlite3", delete=False)
temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
from app.models import *  # noqa: F401,F403
from app.websocket.manager import manager


client = TestClient(app)


class BattleTokenMovementTests(unittest.TestCase):
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

    def test_dm_can_move_tokens_and_players_receive_updates(self) -> None:
        suffix = uuid4().hex[:8]
        dm_token, _ = self._register_and_login(f"move-dm-{suffix}@example.com", "dm")
        player_token, _ = self._register_and_login(f"move-player-{suffix}@example.com", "player")
        outsider_token, _ = self._register_and_login(f"move-outsider-{suffix}@example.com", "player")

        dm_headers = {"Authorization": f"Bearer {dm_token}"}
        player_headers = {"Authorization": f"Bearer {player_token}"}
        outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

        character_create = client.post(
            "/characters/",
            json={
                "name": "Tarin",
                "race": "Human",
                "class_name": "Rogue",
                "max_hp": 14,
            },
            headers=player_headers,
        )
        self.assertEqual(character_create.status_code, 200, character_create.text)
        character_id = character_create.json()["id"]

        campaign_create = client.post(
            "/campaigns/",
            json={"name": f"Move Campaign {suffix}", "description": "Token move test"},
            headers=dm_headers,
        )
        self.assertEqual(campaign_create.status_code, 200, campaign_create.text)
        campaign_id = campaign_create.json()["id"]

        add_member = client.post(
            f"/campaigns/{campaign_id}/members",
            json={"character_id": character_id},
            headers=dm_headers,
        )
        self.assertEqual(add_member.status_code, 200, add_member.text)

        map_create = client.post(
            f"/campaigns/{campaign_id}/battle-maps",
            json={"name": "Dungeon Floor", "width": 12, "height": 9},
            headers=dm_headers,
        )
        self.assertEqual(map_create.status_code, 200, map_create.text)
        map_id = map_create.json()["id"]

        token_create = client.post(
            f"/battle-maps/{map_id}/tokens",
            json={"token_type": "character", "character_id": character_id, "x": 2, "y": 3},
            headers=dm_headers,
        )
        self.assertEqual(token_create.status_code, 200, token_create.text)
        token_id = token_create.json()["id"]

        with client.websocket_connect(f"/ws/campaigns/{campaign_id}?token={player_token}") as player_ws:
            self.assertEqual(len(manager.get_connections(campaign_id)), 1)

            move_response = client.patch(
                f"/battle-tokens/{token_id}",
                json={"x": 7, "y": 5},
                headers=dm_headers,
            )
            self.assertEqual(move_response.status_code, 200, move_response.text)
            self.assertEqual(move_response.json()["x"], 7)
            self.assertEqual(move_response.json()["y"], 5)

            player_event = player_ws.receive_json()
            self.assertEqual(
                player_event,
                {"type": "token_moved", "data": {"token_id": token_id, "x": 7, "y": 5}},
            )

        player_move_attempt = client.patch(
            f"/battle-tokens/{token_id}",
            json={"x": 1, "y": 1},
            headers=player_headers,
        )
        self.assertEqual(player_move_attempt.status_code, 403, player_move_attempt.text)

        outsider_move_attempt = client.patch(
            f"/battle-tokens/{token_id}",
            json={"x": 1, "y": 1},
            headers=outsider_headers,
        )
        self.assertEqual(outsider_move_attempt.status_code, 403, outsider_move_attempt.text)

        state_response = client.get(f"/campaigns/{campaign_id}/state", headers=player_headers)
        self.assertEqual(state_response.status_code, 200, state_response.text)
        state = state_response.json()
        self.assertEqual(state["battle_maps"][0]["id"], map_id)
        self.assertEqual(state["battle_maps"][0]["tokens"][0]["id"], token_id)
        self.assertEqual(state["battle_maps"][0]["tokens"][0]["x"], 7)
        self.assertEqual(state["battle_maps"][0]["tokens"][0]["y"], 5)


if __name__ == "__main__":
    unittest.main()
