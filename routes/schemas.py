from typing import List
from fastapi import APIRouter, HTTPException

from services.schemas import (
    fetch_all_issuer_schema_details,
    fetch_issuer_schema_id_list,
    fetch_schema_details_by_id,
    create_schema,
    CreateSchemaRequest,
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



@router.post("/issuer/create-can-cuoc-cong-dan")
async def create_can_cuoc_cong_dan_schema():
    try:
        schema_data = CreateSchemaRequest(
            schema_name="Can_Cuoc_Cong_Dan",
            schema_version="1.0",
            attributes=[
                "so_cccd", "ho_ten", "ngay_sinh", "gioi_tinh", "quoc_tich",
                "que_quan", "noi_thuong_tru", "ngay_cap", "noi_cap", "unixdob"
            ]
        )
        result = await create_schema(schema_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Can_Cuoc_Cong_Dan schema: {str(e)}") from e
    
    
    
@router.post("/issuer/create-bang-tot-nghiep")
async def create_bang_tot_nghiep_schema():
    try:
        schema_data = CreateSchemaRequest(
            schema_name="Bang_tot_nghiep",
            schema_version="1.0",
            attributes=[
                "unixdob", "ho_ten", "loai_bang", "ngay_sinh", "ngay_tot_nghiep",
                "mssv", "truong", "chuyen_nganh", "gpa", "trang_thai_tot_nghiep"
            ]
        )
        result = await create_schema(schema_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Bang_tot_nghiep schema: {str(e)}") from e
    


@router.post("/issuer/create")
async def create_custom_schema(schema: CreateSchemaRequest):
    try:
        result = await create_schema(schema)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schema: {str(e)}") from e