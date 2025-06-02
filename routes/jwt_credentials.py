from fastapi import APIRouter, HTTPException
from services.jwt_credentials import (
    CreateDidRequest, CreateDidResponse,
    SignVcJwtRequest, SignVcJwtResponse,
    SignVpJwtRequest, SignVpJwtResponse,
    VerifyJwtRequest, VerifyJwtResponse,
    create_did, sign_vc_jwt, sign_vp_jwt, verify_jwt
)

router = APIRouter()

@router.post("/create-did", response_model=CreateDidResponse)
async def create_did_route(request: CreateDidRequest):
    return await create_did(request)

@router.post("/sign-vc-jwt", response_model=SignVcJwtResponse)
async def sign_vc_jwt_route(request: SignVcJwtRequest):
    return await sign_vc_jwt(request)

@router.post("/sign-vp-jwt", response_model=SignVpJwtResponse)
async def sign_vp_jwt_route(request: SignVpJwtRequest):
    return await sign_vp_jwt(request)

@router.post("/verify-jwt", response_model=VerifyJwtResponse)
async def verify_jwt_route(request: VerifyJwtRequest):
    return await verify_jwt(request)