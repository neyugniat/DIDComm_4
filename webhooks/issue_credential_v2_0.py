import json
from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.issue_credential_v2_0")

@router.post("/")
async def issue_credential_webhook(request: Request):
    try:
        payload = await request.json()
        cred_ex_id = payload.get("cred_ex_id")
        # logger.info(f"=================================================================")
        # logger.info(f"Received issue_credential_v2_0 webhook: cred_ex_id={cred_ex_id}, state={payload.get('state')}")
        # logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        # logger.info(f"=================================================================")
        
        # Store in Redis
        redis = request.app.state.redis
        cred_ex_key = f"cred_ex:{cred_ex_id}"

        if await redis.exists(cred_ex_key):
            # logger.warning(f"Duplicate credential exchange ignored: {cred_ex_id}")
            return {"status": "duplicate", "detail": "Credential exchange already processed"}

        await redis.setex(cred_ex_key, 3600, "processed")
        await redis.rpush("webhook:issue_credential_v2_0", json.dumps(payload))
        await redis.publish("cred:events", json.dumps(payload))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing issue_credential_v2_0 webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}