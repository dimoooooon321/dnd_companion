import os
import sys
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4


temp_db = tempfile.NamedTemporaryFile(prefix="dnd_scenes_", suffix=".sqlite3", delete=False)
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


class CampaignSceneFlowTests(unittest.TestCase):
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

    def test_campaign_scene_flow(self) -> None:
        suffix = uuid4().hex[:8]
        dm_token, _ = self._register_and_login(f"scene-dm-{suffix}@example.com", "dm")
        player_token, _ = self._register_and_login(f"scene-player-{suffix}@example.com", "player")
        outsider_token, _ = self._register_and_login(f"scene-outsider-{suffix}@example.com", "player")

        dm_headers = {"Authorization": f"Bearer {dm_token}"}
        player_headers = {"Authorization": f"Bearer {player_token}"}
        outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

        campaign_create = client.post(
            "/campaigns/",
            json={"name": f"Scene Forge {suffix}", "description": "Scene test"},
            headers=dm_headers,
        )
        self.assertEqual(campaign_create.status_code, 200, campaign_create.text)
        campaign_id = campaign_create.json()["id"]

        character_create = client.post(
            "/characters/",
            json={
                "name": "Riven",
                "race": "Human",
                "class_name": "Rogue",
                "max_hp": 14,
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

        scene_create = client.post(
            f"/campaigns/{campaign_id}/scenes",
            json={
                "title": "Hall of Echoes",
                "description": "A long stone hall with whispering statues.",
                "image_url": "https://example.com/hall.png",
            },
            headers=dm_headers,
        )
        self.assertEqual(scene_create.status_code, 200, scene_create.text)
        scene_id = scene_create.json()["id"]
        self.assertFalse(scene_create.json()["is_active"])

        with client.websocket_connect(f"/ws/campaigns/{campaign_id}?token={dm_token}") as dm_ws:
            with client.websocket_connect(
                f"/ws/campaigns/{campaign_id}?token={player_token}"
            ) as player_ws:
                activate = client.patch(
                    f"/campaigns/{campaign_id}/scenes/{scene_id}/activate",
                    headers=dm_headers,
                )
                self.assertEqual(activate.status_code, 200, activate.text)
                self.assertTrue(activate.json()["is_active"])

                player_scene_event = player_ws.receive_json()
                self.assertEqual(
                    player_scene_event,
                    {
                        "type": "scene_changed",
                        "data": {
                            "scene_id": scene_id,
                            "campaign_id": campaign_id,
                            "title": "Hall of Echoes",
                            "description": "A long stone hall with whispering statues.",
                            "image_url": "https://example.com/hall.png",
                            "is_active": True,
                        },
                    },
                )

                scenes_get = client.get(
                    f"/campaigns/{campaign_id}/scenes",
                    headers=player_headers,
                )
                self.assertEqual(scenes_get.status_code, 200, scenes_get.text)
                self.assertEqual(len(scenes_get.json()), 1)
                self.assertEqual(scenes_get.json()[0]["id"], scene_id)

                current_scene = client.get(
                    f"/campaigns/{campaign_id}/current-scene",
                    headers=player_headers,
                )
                self.assertEqual(current_scene.status_code, 200, current_scene.text)
                self.assertEqual(current_scene.json()["id"], scene_id)

                outsider_scenes = client.get(
                    f"/campaigns/{campaign_id}/scenes",
                    headers=outsider_headers,
                )
                self.assertEqual(outsider_scenes.status_code, 403, outsider_scenes.text)

                dm_ws.receive_json()


if __name__ == "__main__":
    unittest.main()
