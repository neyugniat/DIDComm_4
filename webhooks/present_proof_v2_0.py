import json
from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger("webhooks.present_proof_v2_0")

@router.post("/")
async def present_proof_webhook(request: Request):
    try:
        payload = await request.json()
        pres_ex_id = payload.get("pres_ex_id")
        state = payload.get("state")
        verified = payload.get("verified")
        error_msg = payload.get("error_msg")
        role = payload.get("role")
        thread_id = payload.get("thread_id")
        logger.info(f"=================================================================")
        logger.info(f"Received present_proof_v2_0 webhook: pres_ex_id={pres_ex_id}, state={state}, verified={verified}, role={role}, thread_id={thread_id}")
        logger.info(f"=================================================================")

        redis = request.app.state.redis
        pres_key = f"presentation:{thread_id}"

        # Retrieve current presentation data from Redis
        redis_data = await redis.get(pres_key)
        if redis_data:
            presentation_data = json.loads(redis_data)
        else:
            logger.warning(f"No presentation data found for thread_id: {thread_id}")
            # Initialize with default structure if not found
            presentation_data = {
                "thread_id": thread_id,
                "state": state,
                "verifier": {"role": "verifier", "pres_ex_id": None},
                "prover": {"role": "prover", "pres_ex_id": None},
                "error": None,
                "verified": None,
                "credentials": []
            }

        # Update presentation data based on payload
        if role == "prover" and state == "request-received":
            presentation_data["prover"]["pres_ex_id"] = pres_ex_id
        presentation_data["state"] = state

        if role == "verifier" and state == "done" and verified is not None:
            presentation_data["verified"] = verified
            if verified == "false":
                presentation_data["error"] = "Presentation verification failed"
        elif state == "abandoned":
            presentation_data["error"] = error_msg or "Presentation abandoned"

        # Store updated presentation data in Redis
        await redis.setex(pres_key, 3600, json.dumps(presentation_data))
        logger.info(f"Updated presentation data for thread_id: {thread_id}: {json.dumps(presentation_data)}")

        # Store webhook payload for auditing
        await redis.rpush("webhook:events:present_proof_v2_0", json.dumps(payload))
        await redis.publish("publish:events", json.dumps(payload))

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing present_proof_v2_0 webhook: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "detail": str(e)})