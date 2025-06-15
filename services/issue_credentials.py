from typing import Dict, Any, List, Optional
import httpx
import logging

from pydantic import BaseModel, Field
from config import settings

logger = logging.getLogger(__name__)

# Pydantic Models for Send Credential Request
class CredentialPreviewAttribute(BaseModel):
    name: str
    value: str

class CredentialPreview(BaseModel):
    type_: str = Field("issue-credential/2.0/credential-preview", alias="@type") 
    attributes: List[CredentialPreviewAttribute] = Field(...)

class FilterIndy(BaseModel):
    cred_def_id: str
    issuer_did: str
    schema_id: str
    schema_issuer_did: str
    schema_name: str
    schema_version: str

class Filter(BaseModel):
    indy: FilterIndy

class SendCredentialRequest(BaseModel):
    auto_remove: bool
    comment: str
    connection_id: str
    credential_preview: CredentialPreview
    filter: Filter
    trace: bool

# Pydantic Model for Send Credential Response
class SendCredentialResponse(BaseModel):
    cred_ex_id: str
    state: str
    thread_id: str
    cred_preview: CredentialPreview

class CredentialAttribute(BaseModel):
    name: str
    value: str

class CredentialPreview(BaseModel):
    type: str = Field("https://didcomm.org/issue-credential/2.0/credential-preview", alias="@type")
    attributes: List[CredentialAttribute]

class IndyFilter(BaseModel):
    cred_def_id: str

class Filter(BaseModel):
    indy: IndyFilter

class CredentialProposalRequest(BaseModel):
    comment: Optional[str] = "Requesting credential issuance"
    connection_id: str
    credential_preview: CredentialPreview
    filter: Filter
    auto_remove: bool = False

async def send_credential(credential_request: SendCredentialRequest) -> SendCredentialResponse:
    url = f"{settings.ISSUER_AGENT_URL}/issue-credential-2.0/send"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=credential_request.dict(by_alias=True, exclude_unset=True))
            response.raise_for_status()
            logger.info(f"Sent credential to {url}")
            return SendCredentialResponse(**response.json())
    except httpx.RequestError as e:
        logger.error(f"Request error while sending credential to {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while sending credential: {e}")
        raise

async def send_credential_proposal(proposal: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{settings.HOLDER_AGENT_URL}/issue-credential-2.0/send-proposal"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=proposal)
            response.raise_for_status()
            logger.info(f"Sent credential proposal to {url}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while sending credential proposal to {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while sending credential proposal: {e}")
        raise



async def fetch_cred_ex_record(agent: str, cred_ex_id: str) -> Dict[str, Any]:
    if agent.upper() == "ISSUER":
        base_url = settings.ISSUER_AGENT_URL
    elif agent.upper() == "HOLDER":
        base_url = settings.HOLDER_AGENT_URL
    elif agent.upper() == "VERIFIER":
        base_url = settings.VERIFIER_AGENT_URL
    else:
        raise ValueError(f"Unknown agent '{agent}'. Must be one of: issuer, holder, verifier.")

    url = f"{base_url}/issue-credential-2.0/records/{cred_ex_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"[{agent.upper()}] Fetched credential exchange record for {cred_ex_id}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"[{agent.upper()}] Request error while fetching credential exchange record {cred_ex_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"[{agent.upper()}] Unexpected error while fetching credential exchange record: {e}")
        raise


async def fetch_cred_ex_id_list() -> Dict[str, Any]:
    url = f"{settings.HOLDER_AGENT_URL}/issue-credential-2.0/records?count=400&start=0"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            cred_ex_ids = [record.get("cred_ex_record", {}).get("cred_ex_id") for record in data.get("results", []) if "cred_ex_record" in record]
            return {"cred_ex_id": cred_ex_ids}
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching credential exchange ID list: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching credential exchange ID list: {e}")
        raise

async def delete_cred_ex_record(cred_ex_id: str) -> Dict[str, Any]:
    url = f"{settings.HOLDER_AGENT_URL}/issue-credential-2.0/records/{cred_ex_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()
            logger.info(f"Deleted credential exchange record {cred_ex_id}")
            return {"status": "success", "message": f"Credential exchange record {cred_ex_id} deleted"}
    except httpx.RequestError as e:
        logger.error(f"Request error while deleting credential exchange record {cred_ex_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting credential exchange record: {e}")
        raise

async def delete_all_cred_ex_records() -> List[str]:
    try:
        result = await fetch_cred_ex_id_list()
        cred_ex_ids = result.get("cred_ex_id", [])

        deleted_ids = []
        for cred_ex_id in cred_ex_ids:
            try:
                await delete_cred_ex_record(cred_ex_id)
                deleted_ids.append(cred_ex_id)
            except Exception as e:
                logger.error(f"Failed to delete cred_ex_id {cred_ex_id}: {e}")
                continue

        return deleted_ids
    except Exception as e:
        logger.error(f"Failed to delete all credential exchange records: {e}")
        raise