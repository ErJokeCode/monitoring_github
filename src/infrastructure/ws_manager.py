from typing import Any
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
    
    async def connect(self, id: str, ws: WebSocket):
        await ws.accept()
        self.connections[id] = ws
        
    def disconnect(self, id: str):
        self.connections.pop(id)
    
    async def receive_text(self, ws: WebSocket):
        data = await ws.receive_text()
        
    async def broadcast(self, message: dict[str, Any]):
        for ws in self.connections.values():
            await ws.send_json(message)