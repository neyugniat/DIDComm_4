from typing import Dict, Any, List
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

async def send_presentation_request(request: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{settings.VERIFIER_AGENT_URL}/present-proof-2.0/send-request"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request)
            response.raise_for_status()
            logger.info(f"Sent presentation request to {url}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while sending presentation request to {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while sending presentation request: {e}")
        raise
    
    
    
async def fetch_holder_credentials(pres_ex_id: str) -> Dict[str, Any]:
    url = f"{settings.HOLDER_AGENT_URL}/present-proof-2.0/records/{pres_ex_id}/credentials"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Fetched holder credentials for presentation exchange {pres_ex_id}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching holder credentials for {pres_ex_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching holder credentials: {e}")
        raise
    
    
    
async def send_presentation(pres_ex_id: str, presentation: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{settings.HOLDER_AGENT_URL}/present-proof-2.0/records/{pres_ex_id}/send-presentation"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=presentation)
            response.raise_for_status()
            logger.info(f"Sent presentation to {url}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while sending presentation to {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while sending presentation: {e}")
        raise



async def fetch_pres_ex_record(pres_ex_id: str) -> Dict[str, Any]:
    url = f"{settings.VERIFIER_AGENT_URL}/present-proof-2.0/records/{pres_ex_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Fetched presentation exchange record for {pres_ex_id}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching presentation exchange record {pres_ex_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching presentation exchange record: {e}")
        raise
    
    
    
async def fetch_pres_ex_id_list() -> Dict[str, Any]:
    url = f"{settings.VERIFIER_AGENT_URL}/present-proof-2.0/records"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info("Fetched presentation exchange ID list")

            pres_ex_ids = [record.get("pres_ex_id") for record in data.get("results", []) if "pres_ex_id" in record]

            return {"pres_ex_id": pres_ex_ids}
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching presentation exchange ID list: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching presentation exchange ID list: {e}")
        raise



async def delete_pres_ex_record(pres_ex_id: str) -> Dict[str, Any]:
    url = f"{settings.VERIFIER_AGENT_URL}/present-proof-2.0/records/{pres_ex_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()
            logger.info(f"Deleted presentation exchange record {pres_ex_id}")
            return {"status": "success", "message": f"Presentation exchange record {pres_ex_id} deleted"}
    except httpx.RequestError as e:
        logger.error(f"Request error while deleting presentation exchange record {pres_ex_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting presentation exchange record: {e}")
        raise
    
    
    
async def delete_all_pres_ex_records() -> List[str]:
    try:
        result = await fetch_pres_ex_id_list()
        pres_ex_ids = result.get("pres_ex_id", [])

        deleted_ids = []
        for pres_ex_id in pres_ex_ids:
            try:
                await delete_pres_ex_record(pres_ex_id)
                deleted_ids.append(pres_ex_id)
            except Exception as e:
                logger.error(f"Failed to delete pres_ex_id {pres_ex_id}: {e}")
                continue

        return deleted_ids

    except Exception as e:
        logger.error(f"Failed to delete all presentation exchange records: {e}")
        raise