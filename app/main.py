from fastapi import FastAPI

#это последний добавленный
from app.api import characters
from app.api import monsters
from app.api import items
from app.api import item_requests

from app.api import campaigns
from app.api import websocket as websocket_api
# это первый добавленный
from app.api import auth


app = FastAPI(
    title="DnD Companion"
)


app.include_router(
    auth.router
)

app.include_router(
    campaigns.router
)

app.include_router(
    characters.router
)

app.include_router(
    monsters.router
)

app.include_router(
    items.router
)

app.include_router(
    item_requests.router
)

app.include_router(
    websocket_api.router
)

@app.get("/")
def root():
    return {
        "status": "ok"
    }
