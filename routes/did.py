from fastapi import APIRouter
from services.did import get_published_did
from config import settings

router = APIRouter()

@router.get("/issuer", response_model=dict)
async def get_issuer_did():
    did = await get_published_did(settings.ISSUER_AGENT_URL)
    return {"did": did}

@router.get("/holder", response_model=dict)
async def get_holder_did():
    did = await get_published_did(settings.HOLDER_AGENT_URL)
    return {"did": did}

@router.get("/verifier", response_model=dict)
async def get_verifier_did():
    did = await get_published_did(settings.VERIFIER_AGENT_URL)
    return {"did": did}