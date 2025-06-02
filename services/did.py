from typing import Optional
import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_published_did(agent_url: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{agent_url}/wallet/did",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            published_did = next(
                (item["did"] for item in data.get("results", []) if item.get("posture") == "posted"),
                None
            )
            
            if not published_did:
                logger.warning(f"No published DID found for agent at {agent_url}")
                raise HTTPException(status_code=404, detail="No published DID found")
                
            logger.info(f"Retrieved published DID: {published_did} from {agent_url}")
            return published_did
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching DID from {agent_url}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch DID: {e.response.text}")
    except Exception as e:
        logger.error(f"Error fetching DID from {agent_url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching DID: {str(e)}")