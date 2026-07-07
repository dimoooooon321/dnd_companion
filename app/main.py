from fastapi import FastAPI

app = FastAPI(
    title="DnD Companion"
)


@app.get("/")
def root():
    return {
        "status": "ok"
    }