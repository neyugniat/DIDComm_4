from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import aioredis
from config import settings
import logging

router = APIRouter()
logger = logging.getLogger("routes.websocket")

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat updates."""
    await websocket.accept()
    logger.info("Chat WebSocket connected")

    # Subscribe to Redis pub/sub for basicmessages
    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("chat:messages")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_json({"message": message["data"]})
    except WebSocketDisconnect:
        logger.info("Chat WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Server error")
    finally:
        await pubsub.unsubscribe("chat:messages")
        await redis.close()