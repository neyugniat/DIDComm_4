import json
import os
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, List
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

WALLET_FILE = "wallet.json"

class StoreCredentialRequest(BaseModel):
    did: str
    jwt: str
    verkey: str

class Credential(BaseModel):
    did: str
    jwt: str
    verkey: str

def load_wallet() -> List[Dict]:
    try:
        if os.path.exists(WALLET_FILE):
            with open(WALLET_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading wallet: {str(e)}")
        return []

def save_wallet(credentials: List[Dict]):
    try:
        with open(WALLET_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving wallet: {str(e)}")

async def store_credential(request: StoreCredentialRequest) -> Credential:
    try:
        # Verify DID exists in ACA-Py agent
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HOLDER_AGENT_URL}/wallet/did",
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch DIDs: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch DIDs")
            dids = response.json().get("results", [])
            if not any(d["did"] == request.did for d in dids):
                raise HTTPException(status_code=400, detail=f"DID {request.did} not found in agent")

        # Load existing credentials
        credentials = load_wallet()

        # Add new credential (allow multiple DIDs)
        credentials.append({
            "did": request.did,
            "jwt": request.jwt,
            "verkey": request.verkey
        })

        # Save to file
        save_wallet(credentials)
        logger.info(f"Stored credential for DID: {request.did}")
        return Credential(did=request.did, jwt=request.jwt, verkey=request.verkey)
    except Exception as e:
        logger.error(f"Error storing credential: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing credential: {str(e)}")

async def get_credentials() -> List[Credential]:
    try:
        # Fetch DIDs from ACA-Py agent
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HOLDER_AGENT_URL}/wallet/did",
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch DIDs: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch DIDs")
            dids = response.json().get("results", [])

        # Load credentials from file
        credentials = load_wallet()

        # Filter credentials with valid DIDs
        valid_credentials = [
            Credential(did=c["did"], jwt=c["jwt"], verkey=c["verkey"])
            for c in credentials if any(d["did"] == c["did"] for d in dids)
        ]
        logger.info(f"Retrieved {len(valid_credentials)} credentials")
        return valid_credentials
    except Exception as e:
        logger.error(f"Error retrieving credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving credentials: {str(e)}")