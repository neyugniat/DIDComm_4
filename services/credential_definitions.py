from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class CredentialDefinition(BaseModel):
    credential_definition_id: str
    schema_id: Optional[str] = None
    tag: Optional[str] = None
    
class CreateCredDefRequest(BaseModel):
    schema_id: str
    support_revocation: bool = False
    tag: Optional[str] = None

class CreateCredDefResponse(BaseModel):
    credential_definition_id: str


async def create_credential_definition(cred_def: CreateCredDefRequest) -> CreateCredDefResponse:
    url = f"{settings.ISSUER_AGENT_URL}/credential-definitions"
    payload = cred_def.dict(exclude_none=True)
    logger.info(f"Sending payload to {url}: {payload}")
    try:
        # Set a higher timeout (e.g., 30 seconds) to handle slow responses
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            response.raise_for_status()
            data = response.json()
            # Extract credential_definition_id from the response
            credential_definition_id = data.get("credential_definition_id") or data.get("sent", {}).get("credential_definition_id")
            if not credential_definition_id:
                raise ValueError("credential_definition_id not found in response")
            logger.info(f"Successfully created credential definition with ID: {credential_definition_id}")
            return CreateCredDefResponse(credential_definition_id=credential_definition_id)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while creating credential definition: {e}, Status: {e.response.status_code}, Body: {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error while creating credential definition: {type(e).__name__}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating credential definition: {type(e).__name__}: {str(e)}")
        raise


async def fetch_credential_definition_id_list(agent_url: str) -> List[CredentialDefinition]:
    url = f"{agent_url}/credential-definitions/created"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            cred_def_ids = data.get("credential_definition_ids", [])
            return [CredentialDefinition(credential_definition_id=cred_def_id) for cred_def_id in cred_def_ids]
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching credential definitions from {agent_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching credential definitions: {e}")
    return []

async def fetch_credential_definition_details(agent_url: str, cred_def_id: str) -> Dict[str, Any]:
    url = f"{agent_url}/credential-definitions/{cred_def_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching credential definition details from {agent_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching credential definition details: {e}")
    return {}

async def fetch_all_issuer_credential_definition_details() -> List[Dict[str, Any]]:
    cred_def_id_list = await fetch_issuer_credential_definition_id_list()
    cred_def_list_details = []
    for cred_def in cred_def_id_list:
        try:
            detail = await fetch_credential_definition_details(settings.ISSUER_AGENT_URL, cred_def.credential_definition_id)
            if detail and 'credential_definition' in detail:
                cred_def_list_details.append(detail)
        except Exception as e:
            logger.error(f"Error fetching details for cred_def_id {cred_def.credential_definition_id}: {e}")
    return cred_def_list_details

async def fetch_issuer_credential_definition_id_list():
    return await fetch_credential_definition_id_list(settings.ISSUER_AGENT_URL)

async def fetch_credential_definition_details_by_id(cred_def_id: str) -> Optional[Dict[str, Any]]:
    try:
        return await fetch_credential_definition_details(settings.ISSUER_AGENT_URL, cred_def_id)
    except Exception as e:
        logger.error(f"Error fetching credential definition details for {cred_def_id}: {e}")
        return None