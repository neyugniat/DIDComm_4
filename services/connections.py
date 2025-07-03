from typing import Dict, List, Optional
from fastapi import HTTPException
import httpx
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class Connection(BaseModel):
    connection_id: str
    their_label: Optional[str] = None
    state: Optional[str] = None
    my_did: Optional[str] = None
    their_did: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CreateInvitationRequest(BaseModel):
    accept: List[str] = ["didcomm/aip1", "didcomm/aip2;env=rfc19"]
    handshake_protocols: List[str] = ["https://didcomm.org/didexchange/1.1"]
    my_label: str = "DIDComm Agent"
    use_public_did: bool = False

class CreateInvitationResponse(BaseModel):
    invitation: Dict
    invitation_url: str
    
class AcceptInvitationRequest(BaseModel):
    invitation: Dict

class AcceptInvitationResponse(BaseModel):
    connection_id: str

class ConnectionsResponse(BaseModel):
    results: List[Connection]

async def create_invitation(agent_url: str, request: CreateInvitationRequest) -> CreateInvitationResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/out-of-band/create-invitation",
                json=request.dict(exclude_none=True),
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Created invitation for {agent_url}: {data['invitation_url']}")
            return CreateInvitationResponse(**data)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error creating invitation for {agent_url}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to create invitation: {e.response.text}")
    except Exception as e:
        logger.error(f"Error creating invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating invitation: {str(e)}")



async def accept_invitation(agent_url: str, request: AcceptInvitationRequest) -> AcceptInvitationResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/out-of-band/receive-invitation",
                json=request.invitation,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received invitation for {agent_url}: {data['connection_id']}")
            return AcceptInvitationResponse(**data)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error receiving invitation for {agent_url}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to receive invitation: {e.response.text}")
    except Exception as e:
        logger.error(f"Error receiving invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error receiving invitation: {str(e)}")



async def fetch_connections(agent_url: str) -> ConnectionsResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{agent_url}/connections", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            connections = [
                Connection(**conn) for conn in data.get("results", []) if conn.get("state") == "active"
            ]
            logger.info(f"Fetched {len(connections)} active connections from {agent_url}")
            return ConnectionsResponse(results=connections)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching connections from {agent_url}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch connections: {e.response.text}")
    except Exception as e:
        logger.error(f"Error fetching connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching connections: {str(e)}")


async def get_issuer_connections() -> ConnectionsResponse:
    return await fetch_connections(settings.ISSUER_AGENT_URL)



async def get_holder_connections() -> ConnectionsResponse:
    return await fetch_connections(settings.HOLDER_AGENT_URL)



async def get_verifier_connections() -> ConnectionsResponse:
    return await fetch_connections(settings.VERIFIER_AGENT_URL)
