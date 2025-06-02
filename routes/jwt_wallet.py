from fastapi import APIRouter
from services.jwt_wallet import StoreCredentialRequest, Credential, store_credential, get_credentials

router = APIRouter()

@router.post("/store", response_model=Credential)
async def store_credential_route(request: StoreCredentialRequest):
    return await store_credential(request)

@router.get("/credentials", response_model=list[Credential])
async def get_credentials_route():
    return await get_credentials()