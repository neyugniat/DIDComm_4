import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.connections")

@router.post("/")
async def connections_webhook(request: Request):
    try:
        connection = await request.json()
        connection_id = connection.get("connection_id")
        logger.info(f'connection: {connection}')
        # Store connection in Redis
        redis = request.app.state.redis
        connection_key = f"connection:{connection_id}"
        
        if await redis.exists(connection_key):
            logger.warning(f"Duplicate connection ignored: {connection_id}")
            return {"status": "duplicate", "detail": "Connection already processed"}
        
        await redis.setex(connection_key, 3600, "processed")
        await redis.rpush("webhook:connections", json.dumps(connection))
        await redis.publish("chat:connections", json.dumps(connection))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing connection webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}