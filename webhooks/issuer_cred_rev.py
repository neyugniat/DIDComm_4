import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.issuer_cred_rev")

@router.post("/")
async def issuer_cred_rev_webhook(request: Request):
    try:
        revocation = await request.json()
        cred_rev_id = revocation.get("cred_rev_id")
        rev_reg_id = revocation.get("rev_reg_id")
        logger.info(f'credential revocation event: {revocation}')
        # Store revocation event in Redis
        redis = request.app.state.redis
        revocation_key = f"cred_rev:{cred_rev_id}:{rev_reg_id}" if rev_reg_id else f"cred_rev:{cred_rev_id}"
        
        if await redis.exists(revocation_key):
            logger.warning(f"Duplicate revocation event ignored: {cred_rev_id}")
            return {"status": "duplicate", "detail": "Revocation event already processed"}
        
        await redis.setex(revocation_key, 3600, "processed")
        await redis.rpush("webhook:issuer_cred_rev", json.dumps(revocation))
        await redis.publish("chat:issuer_cred_rev", json.dumps(revocation))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing issuer_cred_rev webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}