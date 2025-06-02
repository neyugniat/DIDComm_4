import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.basicmessages")

@router.post("/")
async def basicmessages_webhook(request: Request):
    try:
        message = await request.json()
        message_id = message.get("message_id")
        logger.info(f'message: {message}')
        # Store message in Redis
        redis = request.app.state.redis
        message_key = f"message:{message_id}"
        
        if await redis.exists(message_key):
            logger.warning(f"Duplicate message ignored: {message_id}")
            return {"status": "duplicate", "detail": "Message already processed"}
        
        await redis.setex(message_key, 3600, "processed")
        await redis.rpush("webhook:basicmessages", json.dumps(message))
        await redis.publish("chat:messages", json.dumps(message))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing basicmessage webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}
