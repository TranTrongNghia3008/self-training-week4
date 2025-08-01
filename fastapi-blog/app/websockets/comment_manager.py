from typing import Dict, List
from fastapi import WebSocket

class CommentConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, post_id: int):
        await websocket.accept()
        if post_id not in self.active_connections:
            self.active_connections[post_id] = []
        self.active_connections[post_id].append(websocket)
        print(f"CONNECTED WS: post_id={post_id}, total={len(self.active_connections[post_id])}")

    def disconnect(self, websocket: WebSocket, post_id: int):
        if post_id in self.active_connections:
            self.active_connections[post_id].remove(websocket)
            if not self.active_connections[post_id]: 
                del self.active_connections[post_id]

    async def broadcast(self, post_id: int, message: dict):
        print(f"Connected WS for post_id {post_id} {message}")
        print(self.active_connections)
        if post_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections.get(post_id, []):
                try:
                    print(f"Sending message to websocket: {connection}")
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            for conn in disconnected:
                self.disconnect(conn, post_id)

comment_manager = CommentConnectionManager()