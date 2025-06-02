import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

async def get_wallet_credentials():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.HOLDER_AGENT_URL}/credentials")
            response.raise_for_status()
            return response.json().get("results", [])
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch credentials: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Failed to fetch credentials: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching credentials: {str(e)}")
        raise Exception(f"Error fetching credentials: {str(e)}")
    
async def get_wallet_credential_by_id(credential_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.HOLDER_AGENT_URL}/credential/{credential_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch credential {credential_id}: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Failed to fetch credential {credential_id}: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching credential {credential_id}: {str(e)}")
        raise Exception(f"Error fetching credential {credential_id}: {str(e)}")