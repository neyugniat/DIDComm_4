from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request
import httpx
from pydantic import BaseModel
from services.presentations import (
    delete_all_pres_ex_records,
    delete_pres_ex_record,
    fetch_pres_ex_id_list,
    send_presentation_request, 
    fetch_pres_ex_record,
    fetch_holder_credentials
)
import logging
import json
import time

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_verifier_connection_id_for_holder():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:5000/connections/verifier")
            response.raise_for_status()
            connections = response.json().get("results", [])
            logger.info(f"connections: {connections}")

        except httpx.HTTPStatusError as e:
            raise HTTPException(500, f"Failed to fetch connections: {e.response.status_code}")
        except httpx.RequestError as e:
            raise HTTPException(500, f"Failed to connect to verifier: {str(e)}")
        except httpx.DecodingError:
            raise HTTPException(500, "Invalid JSON response from verifier")
        
        for conn in connections:
            if conn.get("state") == "active":
                return conn["connection_id"]
        raise HTTPException(404, "No active connection found with holder")


@router.post(
    "/send-request",
    summary="Send Presentation Request",
    description="Send a presentation request to the holder agent."
)
async def send_presentation_request_endpoint(request: Request):
    try:
        # Dynamically fetch the connection_id
        connection_id = await get_verifier_connection_id_for_holder()
        
        # Use the fetched connection_id in the proof_request
        proof_request = {
            "connection_id": connection_id,
            "auto_verify": True,
            "presentation_request": {
                "indy": {
                    "name": "Proof of Name",
                    "version": "1.0",
                    "requested_attributes": {
                        "name_attr": {"name": "ten"}
                    },
                    "requested_predicates": {},
                    "non_revoked": {"from": 0, "to": int(time.time())}
                }
            },
            "auto_remove": False
        }
        
        # Send the presentation request (assuming this function is defined elsewhere)
        response = await send_presentation_request(proof_request)
        verifier_pres_ex_id = response.get("pres_ex_id")
        thread_id = response.get("thread_id")
        logger.info(f"Presentation request sent successfully: {response}")
        
        # Validate response
        if not verifier_pres_ex_id or not thread_id:
            raise ValueError("Missing pres_ex_id or thread_id")
        
        # Prepare and store presentation data in Redis
        presentation_data = {
            "thread_id": thread_id,
            "verifier": {
                "role": "verifier",
                "pres_ex_id": verifier_pres_ex_id
            },
            "prover": {
                "role": "prover",
                "pres_ex_id": None
            }
        }
        redis = request.app.state.redis
        await redis.setex(f"presentation:{thread_id}", 3600, json.dumps(presentation_data))
        logger.info(f"Stored presentation data for thread_id {thread_id}: {presentation_data}")
        
        return response
    except HTTPException as e:
        raise e  # Re-raise HTTP-specific exceptions
    except Exception as e:
        logger.error(f"Failed to send presentation request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send presentation request: {str(e)}")



@router.get("/fetch_record/{pres_ex_id}",
    summary="Fetch Presentation Exchange Record",
    description="Fetch the presentation exchange record by its ID."
)
async def fetch_presentation_exchange_record(pres_ex_id: str, request: Request):
    try:
        record = await fetch_pres_ex_record(pres_ex_id)
        if not record:
            raise HTTPException(status_code=404, detail="Presentation exchange record not found")
        return record
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching presentation exchange record {pres_ex_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e



@router.get(
    "/get-presentation-status/{thread_id}",
    summary="Get Presentation Status",
    description="Retrieve the status of a presentation exchange by thread ID from Redis."
)
async def get_presentation_status(thread_id: str, request: Request):
    try:
        redis = request.app.state.redis
        pres_key = f"presentation:{thread_id}"
        redis_data = await redis.get(pres_key)
        if not redis_data:
            logger.warning(f"No presentation data found for thread_id: {thread_id}")
            raise HTTPException(status_code=404, detail="Presentation data not found for the given thread ID")

        try:
            presentation_data = json.loads(redis_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data in Redis for {pres_key}: {redis_data}, error: {str(e)}")
            raise HTTPException(status_code=500, detail="Invalid presentation data stored in Redis")

        logger.info(f"Retrieved presentation status for thread_id: {thread_id}")
        return presentation_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving presentation status for thread_id {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presentation status: {str(e)}")
   
   
    
@router.get(
    "/verify/{thread_id}",
    summary="Verify Presentation by Thread ID",
    description="Check if the presentation is verified by thread ID."
)
async def verify_presentation(thread_id: str, request: Request):
    try:
        redis = request.app.state.redis
        pres_key = f"presentation:{thread_id}"
        redis_data = await redis.get(pres_key)
        if not redis_data:
            logger.warning(f"No presentation data found for thread_id: {thread_id}")
            raise HTTPException(status_code=404, detail="Presentation data not found for the given thread ID")

        try:
            presentation_data = json.loads(redis_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data in Redis for {pres_key}: {redis_data}, error: {str(e)}")
            raise HTTPException(status_code=500, detail="Invalid presentation data stored in Redis")

        state = presentation_data.get("state")
        verified = presentation_data.get("verified")
        error = presentation_data.get("error")

        if state in ["done", "deleted"]:
            if verified == "true":
                return {"status": "verified"}
            elif verified == "false":
                return {"status": "failed", "error": error or "Verification failed"}
        elif state == "abandoned":
            raise HTTPException(status_code=400, detail={"status": "abandoned", "error": error or "Presentation abandoned"})
        else:
            raise HTTPException(status_code=425, detail={"status": "pending", "error": "Verification still in progress"})

        logger.info(f"Verification status for thread_id {thread_id}: {state}, verified={verified}")
        return presentation_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying presentation for thread_id {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify presentation: {str(e)}")
    
    
    
@router.get(
    "/fetch_pres_ex_id_list",
    summary="Fetch Presentation Exchange ID List",
    description="Retrieve a list of all presentation exchange IDs."
)
async def fetch_pres_ex_id_list_endpoint() -> Dict[str, Any]:
    try:
        pres_ex_id_list = await fetch_pres_ex_id_list()
        if not pres_ex_id_list:
            raise HTTPException(status_code=404, detail="No presentation exchange IDs found")
        return pres_ex_id_list
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching presentation exchange ID list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
    
    
@router.delete(
    "/delete_pres_ex_record/{pres_ex_id}",
    summary="Delete Presentation Exchange Record",
    description="Delete a presentation exchange record by its ID."
)
async def delete_pres_ex_record_endpoint(pres_ex_id: str) -> Dict[str, Any]:
    try:
        result = await delete_pres_ex_record(pres_ex_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting presentation exchange record {pres_ex_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/delete_pres_ex_record",
    summary="Delete All Presentation Exchange Records",
    description="Delete all presentation exchange records."
)
async def delete_all_pres_ex_records_endpoint() -> Dict[str, Any]:
    try:
        deleted_ids = await delete_all_pres_ex_records()
        
        return {
            "message": f"Deleted {len(deleted_ids)} presentation exchange records.",
            "deleted_pres_ex_ids": deleted_ids
        }
    except Exception as e:
        logger.error(f"Error deleting all presentation exchange records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e