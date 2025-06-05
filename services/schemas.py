from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class Schema(BaseModel):
    schema_id: str

class CredentialDefinition(BaseModel):
    credential_definition_id: str
    schema_id: str
    tag: Optional[str] = None

class CreateSchemaRequest(BaseModel):
    schema_name: str
    schema_version: str
    attributes: List[str]

class SchemaDetails(BaseModel):
    ver: str
    id: str
    name: str
    version: str
    attrNames: List[str]
    seqNo: int

class CreateSchemaResponse(BaseModel):
    sent: Dict[str, Any]
    schema_id: str
    schema_details: SchemaDetails  

async def fetch_schema_id_list(agent_url: str) -> List[Schema]:
    url = f"{agent_url}/schemas/created"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            schema_ids = data.get("schema_ids", [])
            return [Schema(schema_id=schema_id) for schema_id in schema_ids]
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching schemas from {agent_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching schemas: {e}")
    return []

async def fetch_schema_details(agent_url: str, schema_id: str) -> Dict[str, Any]:
    url = f"{agent_url}/schemas/{schema_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching schema details from {agent_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching schema details: {e}")
    return {}

async def fetch_all_issuer_schema_details() -> List[Dict[str, Any]]:
    schema_id_list = await fetch_issuer_schema_id_list()
    schema_details_list = []
    for schema in schema_id_list:
        details = await fetch_schema_details(settings.ISSUER_AGENT_URL, schema.schema_id)
        if details:
            schema_details_list.append(details)
    return schema_details_list

async def fetch_issuer_schema_id_list():
    return await fetch_schema_id_list(settings.ISSUER_AGENT_URL)

async def fetch_schema_details_by_id(schema_id: str) -> Optional[Dict[str, Any]]:
    try:
        return await fetch_schema_details(settings.ISSUER_AGENT_URL, schema_id)
    except Exception as e:
        logger.error(f"Error fetching schema details for {schema_id}: {e}")
        return None

async def create_schema(schema: CreateSchemaRequest) -> CreateSchemaResponse:
    url = f"{settings.ISSUER_AGENT_URL}/schemas"
    payload = schema.dict()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully created schema with schema_id: {data.get('schema_id')}")
            data['schema_details'] = data.pop('schema')
            return CreateSchemaResponse(**data)
    except httpx.RequestError as e:
        logger.error(f"Request error while creating schema: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating schema: {e}")
        raise