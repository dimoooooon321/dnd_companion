import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import engine
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

dm_token = dm_login.json()["access_token"]
dm_headers = {"Authorization": f"Bearer {dm_token}"}

campaign_create = client.post(
    "/campaigns/",
    json={"name": f"Forge of Dawn {suffix}", "description": "Main test campaign"},
    headers=dm_headers,
)
print("campaign_create", campaign_create.status_code, campaign_create.json())

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

player_token = player_login.json()["access_token"]
player_headers = {"Authorization": f"Bearer {player_token}"}

player_campaign_create = client.post(
    "/campaigns/",
    json={"name": "Player Attempt"},
    headers=player_headers,
)
print("player_campaign_create", player_campaign_create.status_code, player_campaign_create.json())

with engine.connect() as connection:
    dm_rows = connection.execute(
        text("SELECT id, email, role FROM users WHERE email = :email"),
        {"email": dm_email},
    ).fetchall()
    player_rows = connection.execute(
        text("SELECT id, email, role FROM users WHERE email = :email"),
        {"email": player_email},
    ).fetchall()
    campaigns = connection.execute(
        text("SELECT id, name, dm_id FROM campaigns WHERE name = :name"),
        {"name": f"Forge of Dawn {suffix}"},
    ).fetchall()
    print("db_dm_users", dm_rows)
    print("db_player_users", player_rows)
    print("db_campaigns", campaigns)
