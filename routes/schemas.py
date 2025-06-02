from typing import List
from fastapi import APIRouter, HTTPException

from services.schemas import (
    fetch_all_issuer_schema_details,
    fetch_issuer_schema_id_list,
    fetch_schema_details_by_id
)

router = APIRouter()

@router.get("/issuer")
async def issuer_schemas():
    try: 
        return await fetch_issuer_schema_id_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/issuer/{schema_id}")
async def issuer_schema_details(schema_id: str):
    try:
        details = await fetch_schema_details_by_id(schema_id)
        if details:
            return details
        raise HTTPException(status_code=404, detail="Schema not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/issuer/all")
async def issuer_schema_details():
    try:
        return await fetch_all_issuer_schema_details()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
