from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel
from fastapi import HTTPException
from config import settings
from redis.asyncio import Redis
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class RequestedAttribute(BaseModel):
    name: str
    restrictions: Optional[List[Dict[str, str]]] = None

class RequestedPredicate(BaseModel):
    name: str
    p_type: str
    p_value: int
    restrictions: Optional[List[Dict[str, str]]] = None

class PresentationRequestIndy(BaseModel):
    name: str
    version: str
    requested_attributes: Dict[str, RequestedAttribute]
    requested_predicates: Dict[str, RequestedPredicate]
    non_revoked: Optional[Dict[str, int]] = None

class PresentationRequest(BaseModel):
    indy: PresentationRequestIndy

class SendProofRequest(BaseModel):
    connection_id: str
    auto_verify: bool = True
    presentation_request: PresentationRequest
    auto_remove: bool = False

class SendProofResponse(BaseModel):
    pres_ex_id: str
    thread_id: str
    role: str
    holder_pres_ex_id: Optional[str] = None
    credentials: Optional[List[Dict]] = None

class CredentialInfo(BaseModel):
    referent: str
    schema_id: str
    cred_def_id: str
    rev_reg_id: Optional[str] = None
    cred_rev_id: Optional[str] = None
    attrs: Dict[str, str]

class CredentialInterval(BaseModel):
    from_: Optional[int] = None
    to: Optional[int] = None

class PresentationCredential(BaseModel):
    cred_info: CredentialInfo
    interval: Optional[CredentialInterval] = None
    presentation_referents: List[str]

class PresentationCredentialsResponse(BaseModel):
    results: List[PresentationCredential]

class RequestedAttributePresentation(BaseModel):
    cred_id: str
    revealed: bool

class IndyPresentation(BaseModel):
    requested_attributes: Dict[str, RequestedAttributePresentation]
    requested_predicates: Dict[str, Dict[str, str]]
    self_attested_attributes: Dict = {}

class PresentationFormat(BaseModel):
    indy: IndyPresentation

class SendPresentationRequest(BaseModel):
    pres_ex_id: str
    presentation: PresentationFormat

class SendPresentationResponse(BaseModel):
    pres_ex_id: str
    thread_id: str
    state: str

async def send_proof_request(redis: Redis, request: SendProofRequest) -> SendProofResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.VERIFIER_AGENT_URL}/present-proof-2.0/send-request",
                json=request.dict(exclude_none=True),
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Sent proof request: {data['pres_ex_id']}")

            result = SendProofResponse(
                pres_ex_id=data["pres_ex_id"],
                thread_id=data["thread_id"],
                role=data["role"]
            )

            redis_key = f"presentation:{result.thread_id}"
            await redis.setex(
                redis_key,
                3600,
                json.dumps({
                    "thread_id": result.thread_id,
                    "state": data["state"],
                    "verifier": {"role": "verifier", "pres_ex_id": result.pres_ex_id},
                    "prover": {"role": "prover", "pres_ex_id": None},
                    "error": None,
                    "verified": None,
                    "credentials": []
                })
            )
            logger.info(f"Stored presentation {result.pres_ex_id} in Redis under {redis_key}")

            for _ in range(5):
                redis_data = await redis.get(redis_key)
                if redis_data:
                    presentation_data = json.loads(redis_data)
                    if presentation_data["prover"]["pres_ex_id"]:
                        holder_pres_ex_id = presentation_data["prover"]["pres_ex_id"]
                        result.holder_pres_ex_id = holder_pres_ex_id
                        credentials_response = await fetch_presentation_credentials(redis, holder_pres_ex_id)
                        presentation_data["credentials"] = [cred.dict() for cred in credentials_response.results]
                        await redis.setex(redis_key, 3600, json.dumps(presentation_data))
                        logger.info(f"Stored credentials for {holder_pres_ex_id} in Redis")
                        result.credentials = [cred.dict() for cred in credentials_response.results]
                        break
                await asyncio.sleep(1)

            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending proof request: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to send proof request: {e.response.text}")
    except Exception as e:
        logger.error(f"Error sending proof request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending proof request: {str(e)}")

async def fetch_presentation_credentials(redis: Redis, pres_ex_id: str) -> PresentationCredentialsResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HOLDER_AGENT_URL}/present-proof-2.0/records/{pres_ex_id}/credentials",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            credentials = [PresentationCredential(**cred) for cred in data]
            logger.info(f"Fetched {len(credentials)} credentials for pres_ex_id: {pres_ex_id}")
            return PresentationCredentialsResponse(results=credentials)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching credentials for {pres_ex_id}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch credentials: {e.response.text}")
    except Exception as e:
        logger.error(f"Error fetching credentials for {pres_ex_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch credentials: {str(e)}")

async def send_presentation(redis: Redis, request: SendPresentationRequest) -> SendPresentationResponse:
    try:
        payload = {
            "pres_ex_id": request.pres_ex_id,
            "auto_present": False,
            "trace": False
        }
        payload.update(request.presentation.dict(exclude_none=True))
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.HOLDER_AGENT_URL}/present-proof-2.0/records/{request.pres_ex_id}/send-presentation",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Sent presentation for pres_ex_id: {request.pres_ex_id}")

            redis_key = f"presentation:{data['thread_id']}"
            redis_data = await redis.get(redis_key)
            if redis_data:
                presentation_data = json.loads(redis_data)
                presentation_data["state"] = data["state"]
                await redis.setex(redis_key, 3600, json.dumps(presentation_data))
                logger.info(f"Updated presentation state for {data['thread_id']} in Redis")

            return SendPresentationResponse(
                pres_ex_id=data["pres_ex_id"],
                thread_id=data["thread_id"],
                state=data["state"]
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending presentation: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to send presentation: {e.response.text}")
    except Exception as e:
        logger.error(f"Error sending presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending presentation: {str(e)}")