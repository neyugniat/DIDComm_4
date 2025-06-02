from config import settings
from fastapi import APIRouter, HTTPException
from services.connections import (
    CreateInvitationRequest, CreateInvitationResponse,
    AcceptInvitationRequest, AcceptInvitationResponse,
    ConnectionsResponse, get_issuer_connections, get_holder_connections,
    get_verifier_connections, create_invitation, accept_invitation
)

router = APIRouter()

@router.post("/issuer/create-invitation", response_model=CreateInvitationResponse)
async def create_issuer_invitation(request: CreateInvitationRequest):
    return await create_invitation(settings.ISSUER_AGENT_URL, request)



@router.post("/verifier/create-invitation", response_model=CreateInvitationResponse)
async def create_issuer_invitation(request: CreateInvitationRequest):
    return await create_invitation(settings.VERIFIER_AGENT_URL, request)



@router.post("/holder/receive-invitation", response_model=AcceptInvitationResponse)
async def receive_holder_invitation(request: AcceptInvitationRequest):
    return await accept_invitation(settings.HOLDER_AGENT_URL, request)



@router.get("/issuer", response_model=ConnectionsResponse)
async def list_issuer_connections():
    return await get_issuer_connections()

@router.get("/holder", response_model=ConnectionsResponse)
async def list_holder_connections():
    return await get_holder_connections()

@router.get("/verifier", response_model=ConnectionsResponse)
async def list_verifier_connections():
    return await get_verifier_connections()