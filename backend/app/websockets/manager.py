from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)

    async def broadcast_to_room(self, message: dict, room: str):
        if room not in self.active_connections:
            return
        dead = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead.append(connection)
        for d in dead:
            if d in self.active_connections[room]:
                self.active_connections[room].remove(d)

    def get_connection_count(self, room: str) -> int:
        return len(self.active_connections.get(room, []))


manager = ConnectionManager()
