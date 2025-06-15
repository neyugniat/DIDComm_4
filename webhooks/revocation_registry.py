import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.revocation_registry")

@router.post("/")
async def revocation_registry_webhook(request: Request):
    try:
        revocation = await request.json()
        rev_reg_id = revocation.get("rev_reg_id")
        # logger.info(f'revocation registry event: {revocation}')
        # Store revocation event in Redis
        redis = request.app.state.redis
        revocation_key = f"revocation:{rev_reg_id}"
        
        if await redis.exists(revocation_key):
            # logger.warning(f"Duplicate revocation event ignored: {rev_reg_id}")
            return {"status": "duplicate", "detail": "Revocation event already processed"}
        
        await redis.setex(revocation_key, 3600, "processed")
        await redis.rpush("webhook:revocation_registry", json.dumps(revocation))
        await redis.publish("chat:revocation_registry", json.dumps(revocation))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing revocation registry webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}