import asyncio
import json
from typing import List, Set
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.core.logger import logger


class WebSocketManager:
    """Manages active real-time dashboard client connections and broadcasts"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        if not self.active_connections:
            return

        payload = json.dumps({"type": event_type, "data": data}, default=str)
        disconnected = []

        for conn in list(self.active_connections):
            try:
                await conn.send_text(payload)
            except Exception:
                disconnected.append(conn)

        for dead in disconnected:
            self.disconnect(dead)


ws_manager = WebSocketManager()
