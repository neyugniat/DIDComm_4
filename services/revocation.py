import asyncio
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class RevocationRegistry(BaseModel):
    rev_reg_id: str

class IssuedCredential(BaseModel):
    state: str
    created_at: str
    updated_at: str
    record_id: str
    cred_ex_id: str
    rev_reg_id: str
    cred_def_id: str
    cred_rev_id: str
    cred_ex_version: str

class RevokeCredentialRequest(BaseModel):
    connection_id: str
    comment: Optional[str] = None
    cred_rev_id: str
    rev_reg_id: str
    notify: bool = True
    publish: bool = True

class RevokeCredentialResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    
async def fetch_revocation_registry_id_list() -> List[RevocationRegistry]:
    url = f"{settings.ISSUER_AGENT_URL}/revocation/registries/created"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            rev_reg_ids = data.get("rev_reg_ids", [])
            return [RevocationRegistry(rev_reg_id=rev_reg_id) for rev_reg_id in rev_reg_ids]
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching revocation registries: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching revocation registries: {e}")
        raise

async def fetch_issued_credentials(rev_reg_id: str) -> List[IssuedCredential]:
    url = f"{settings.ISSUER_AGENT_URL}/revocation/registry/{rev_reg_id}/issued/details"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return [IssuedCredential(**cred) for cred in data]
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching issued credentials for {rev_reg_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching issued credentials for {rev_reg_id}: {e}")
        raise

async def fetch_all_issued_credentials() -> List[IssuedCredential]:
    try:
        # Fetch all revocation registry IDs
        registries = await fetch_revocation_registry_id_list()
        rev_reg_ids = [registry.rev_reg_id for registry in registries]
        
        # Create tasks to fetch issued credentials concurrently
        tasks = [fetch_issued_credentials(rev_reg_id) for rev_reg_id in rev_reg_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all credentials, handling exceptions
        all_credentials = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching credentials: {result}")
            else:
                all_credentials.extend(result)
        return all_credentials
    except Exception as e:
        logger.error(f"Error fetching all issued credentials: {e}")
        raise

async def revoke_credential(revoke_request: RevokeCredentialRequest) -> RevokeCredentialResponse:
    url = f"{settings.ISSUER_AGENT_URL}/revocation/revoke"
    payload = revoke_request.dict(exclude_none=True)
    logger.info(f"Sending payload to {url}: {payload}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            response.raise_for_status()
            data = response.json()
            success = data.get("success", True)
            message = data.get("message", None)
            logger.info(f"Successfully revoked credential: {payload}")
            return RevokeCredentialResponse(success=success, message=message)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while revoking credential: {e}, Status: {e.response.status_code}, Body: {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error while revoking credential: {type(e).__name__}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while revoking credential: {type(e).__name__}: {str(e)}")
        raise