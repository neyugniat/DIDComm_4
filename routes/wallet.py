from fastapi import APIRouter, HTTPException
import logging
from services.wallet import get_wallet_credential_by_id, get_wallet_credentials, get_credential_revocation_status

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/credentials",
    summary="Fetch Holder's Wallet Credentials",
    description="Retrieve all credentials stored in the holder's wallet."
)
async def fetch_wallet_credentials():
    try:
        credentials = await get_wallet_credentials()
        return {"results": credentials}
    except Exception as e:
        logger.error(f"Error in /wallet/credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/credential/{credential_id}",
    summary="Fetch Wallet Credential by ID",
    description="Retrieve a specific credential from the holder's wallet using its ID."
)
async def fetch_wallet_credential_by_id(credential_id: str):
    try:
        credential = await get_wallet_credential_by_id(credential_id)
        if credential:
            return credential
        raise HTTPException(status_code=404, detail="Credential not found")
    except Exception as e:
        logger.error(f"Error in /wallet/credential/{credential_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get(
    "/credential/revoked/{credential_id}",
    summary="Check Credential Revocation Status",
    description="Check if a specific credential in the holder's wallet has been revoked."
)
async def fetch_credential_revocation_status(credential_id: str):
    try:
        status = await get_credential_revocation_status(credential_id)
        return status
    except Exception as e:
        logger.error(f"Error in /wallet/credential/revoked/{credential_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))