import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.events import redis_client

router = APIRouter()

@router.websocket("/ws/agent-feed")
async def agent_feed_ws(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("agent_events")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                await websocket.send_text(message['data'])
            else:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        await pubsub.unsubscribe("agent_events")
        print("Client disconnected from agent feed")
