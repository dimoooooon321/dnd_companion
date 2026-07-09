from __future__ import annotations

from collections.abc import Iterable

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, campaign_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(campaign_id, []).append(websocket)

    def disconnect(self, campaign_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(campaign_id)
        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            self.active_connections.pop(campaign_id, None)

    async def broadcast(self, campaign_id: int, message: dict) -> None:
        for websocket in list(self.active_connections.get(campaign_id, [])):
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(campaign_id, websocket)

    def get_connections(self, campaign_id: int) -> Iterable[WebSocket]:
        return tuple(self.active_connections.get(campaign_id, []))


manager = ConnectionManager()

