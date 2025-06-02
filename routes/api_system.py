from fastapi import APIRouter, HTTPException
from services.api_system import (
    Book, PatientRecord,
    JwtRequest,
    get_book_list, get_patient_records
)
from typing import List, Dict, Any

router = APIRouter()

@router.post(
    "/get-book-list", 
    summary="Get Book List", 
    response_model=List[Book])
async def get_books_list_endpoint(request: JwtRequest):
    return await get_book_list(request)

@router.post(
    "/get-patient-records",
    response_model=List[PatientRecord])
async def get_patient_records_endpoint(request: JwtRequest):
    return await get_patient_records(request)