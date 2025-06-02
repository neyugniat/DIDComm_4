from typing import List
from fastapi import APIRouter, HTTPException
from services.credentials import (
    fetch_credentials,
    fetch_credentials_full,
    delete_credential,
    delete_all_credentials,
    CredentialsResponse,
    DeleteCredentialsResponse,
)

router = APIRouter()

@router.get(
    "/",
    summary="List Holder Credentials",
    description="Fetch all credentials from the holder wallet, including referent IDs and attributes.",
    response_model=CredentialsResponse
)
async def list_credentials() -> CredentialsResponse:
    return await fetch_credentials_full()

@router.get(
    "/referents",
    summary="List Credential Referent IDs",
    description="Fetch only the referent IDs of all credentials in the holder wallet.",
    response_model=List[str]
)
async def list_credential_referents() -> List[str]:
    """
    Retrieve a list of referent IDs for all credentials in the holder wallet.
    """
    return await fetch_credentials()


@router.delete(
    "/credential/{referent}",
    summary="Delete Single Credential",
    description="Delete a single credential from the holder wallet by its referent ID.",
    response_model=dict
)
async def delete_single_credential(referent: str) -> dict:
    """
    Delete a specific credential identified by its referent ID.
    """
    success = await delete_credential(referent)
    if success:
        return {"message": f"Credential {referent} deleted successfully"}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete credential {referent}"
        )

@router.delete(
    "/delete_all_credentials",
    summary="Delete All Holder Credentials",
    description="Delete all credentials in the holder wallet, returning a summary of deleted credentials and any errors.",
    response_model=DeleteCredentialsResponse
)
async def delete_all_holder_credentials() -> DeleteCredentialsResponse:
    """
    Remove all credentials from the holder wallet.
    """
    return await delete_all_credentials()