from fastapi import APIRouter, HTTPException
from typing import List
from services.revocation import (
    fetch_revocation_registry_id_list,
    fetch_issued_credentials,
    revoke_credential,
    RevokeCredentialRequest,
    RevocationRegistry,
    IssuedCredential,
    RevokeCredentialResponse,
    fetch_all_issued_credentials
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/registries", response_model=List[RevocationRegistry])
async def get_revocation_registries():
    """Fetch the list of created revocation registry IDs."""
    try:
        return await fetch_revocation_registry_id_list()
    except Exception as e:
        logger.error(f"Error fetching revocation registries: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/registries/{rev_reg_id}/issued", response_model=List[IssuedCredential])
async def get_issued_credentials(rev_reg_id: str):
    """Fetch the list of issued credentials for a given revocation registry ID."""
    try:
        return await fetch_issued_credentials(rev_reg_id)
    except Exception as e:
        logger.error(f"Error fetching issued credentials for {rev_reg_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/issued-credentials", response_model=List[IssuedCredential])
async def get_all_issued_credentials():
    """Fetch all issued credentials across all revocation registries."""
    try:
        return await fetch_all_issued_credentials()
    except Exception as e:
        logger.error(f"Error fetching all issued credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/revoke", response_model=RevokeCredentialResponse)
async def revoke_credential_route(revoke_request: RevokeCredentialRequest):
    """Revoke a credential with the provided payload."""
    try:
        logger.info(f"revoke_request: {revoke_request}")
        logger.info("Calling revoke_credential")
        result = await revoke_credential(revoke_request)
        return result
    except Exception as e:
        logger.error(f"Error in revoke_credential_route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to revoke credential: {str(e)}") from e