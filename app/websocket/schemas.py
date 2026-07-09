from __future__ import annotations

from pydantic import BaseModel, Field


class WebSocketEvent(BaseModel):
    type: str
    data: dict[str, object] = Field(default_factory=dict)

