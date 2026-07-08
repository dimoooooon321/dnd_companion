from fastapi import FastAPI

#это последний добавленный
from app.api import characters

from app.api import campaigns
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

@app.get("/")
def root():
    return {
        "status": "ok"
    }