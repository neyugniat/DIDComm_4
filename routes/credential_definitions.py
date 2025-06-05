from typing import List
from config import settings
from fastapi import APIRouter, HTTPException
import logging

from services.credential_definitions import (
    fetch_all_issuer_credential_definition_details,
    fetch_issuer_credential_definition_id_list,
    fetch_credential_definition_details_by_id,
    CreateCredDefRequest,
    create_credential_definition
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create")
async def create_cred_def(cred_def: CreateCredDefRequest):
    try:
        logger.info(f"cred_def: {cred_def}")
        logger.info("Calling create_credential_definition")
        result = await create_credential_definition(cred_def)
        return result
    except Exception as e:
        logger.error(f"Error in create_cred_def: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create credential definition: {str(e)}") from e
    
@router.get("/issuer")
async def issuer_credential_definitions():
    try:
        return await fetch_issuer_credential_definition_id_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/issuer/{cred_def_id}")
async def issuer_credential_definition_details(cred_def_id: str):
    try:
        details = await fetch_credential_definition_details_by_id(cred_def_id)
        if details:
            return details
        raise HTTPException(status_code=404, detail="Credential Definition not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/issuer/all")
async def issuer_credential_definition_details():
    try:
        return await fetch_all_issuer_credential_definition_details()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e