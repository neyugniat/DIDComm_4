import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.issue_credential_v2_0_indy")

@router.post("/")
async def issue_credential_v2_0_indy_webhook(request: Request):
    try:
        credential = await request.json()
        cred_ex_id = credential.get("cred_ex_id")
        logger.info(f'credential: {credential}')
        # Store credential in Redis
        redis = request.app.state.redis
        credential_key = f"credential:{cred_ex_id}"
        
        if await redis.exists(credential_key):
            logger.warning(f"Duplicate credential ignored: {cred_ex_id}")
            return {"status": "duplicate", "detail": "Credential already processed"}
        
        await redis.setex(credential_key, 3600, "processed")
        await redis.rpush("webhook:issue_credential_v2_0_indy", json.dumps(credential))
        await redis.publish("chat:issue_credential_v2_0_indy", json.dumps(credential))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing issue_credential_v2_0_indy webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}