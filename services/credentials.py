from typing import List, Dict, Any
import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class Credential(BaseModel):
    referent: str
    schema_id: str
    cred_def_id: str
    rev_reg_id: str | None = None
    cred_rev_id: str | None = None
    attrs: Dict[str, str]

class CredentialsResponse(BaseModel):
    results: List[Credential]

class DeleteCredentialsResponse(BaseModel):
    deleted_count: int
    errors: List[str]

async def fetch_credentials() -> List[str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HOLDER_AGENT_URL}/credentials?count=100&start=0",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            credentials = CredentialsResponse(**data)
            referents = [cred.referent for cred in credentials.results]
            logger.info(f"Fetched {len(referents)} credentials from holder agent")
            return referents
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching credentials: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch credentials: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error fetching credentials: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching credentials: {str(e)}"
        )

async def fetch_credentials_full() -> CredentialsResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HOLDER_AGENT_URL}/credentials?count=100&start=0",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            credentials = CredentialsResponse(**data)
            logger.info(f"Fetched {len(credentials.results)} credentials with full details from holder agent")
            return credentials
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching credentials: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch credentials: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error fetching credentials: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching credentials: {str(e)}"
        )

async def delete_credential(referent: str) -> bool:
    """
    Delete a single credential by referent ID.
    Returns True if successful, False if failed.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{settings.HOLDER_AGENT_URL}/credential/{referent}",
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Deleted credential {referent}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error deleting credential {referent}: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Error deleting credential {referent}: {str(e)}")
        return False

async def delete_all_credentials() -> DeleteCredentialsResponse:
    """
    Delete all credentials in the holder wallet.
    Returns a summary of deleted credentials and any errors.
    """
    try:
        referents = await fetch_credentials()
        deleted_count = 0
        errors = []

        for referent in referents:
            success = await delete_credential(referent)
            if success:
                deleted_count += 1
            else:
                errors.append(f"Failed to delete credential {referent}")

        logger.info(f"Deleted {deleted_count} of {len(referents)} credentials")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during deletion")

        return DeleteCredentialsResponse(
            deleted_count=deleted_count,
            errors=errors
        )
    except Exception as e:
        logger.error(f"Error deleting all credentials: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting all credentials: {str(e)}"
        )