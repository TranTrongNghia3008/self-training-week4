from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.comment_manager import comment_manager

router = APIRouter()

@router.websocket("/comments/{post_id}")
async def comment_websocket(websocket: WebSocket, post_id: int):
    await comment_manager.connect(websocket, post_id)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        comment_manager.disconnect(websocket, post_id)
