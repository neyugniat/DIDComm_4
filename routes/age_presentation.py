from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from services.age_presentation import (
    SendProofRequest, SendProofResponse, send_proof_request,
    fetch_presentation_credentials, PresentationCredentialsResponse,
    SendPresentationRequest, SendPresentationResponse, send_presentation
)
from redis.asyncio import Redis
from config import settings

router = APIRouter()

async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()


@router.post("/verifier/send-request", response_model=SendProofResponse)
async def send_verifier_proof_request(request: SendProofRequest, redis: Redis = Depends(get_redis)):
    return await send_proof_request(redis, request)

@router.get("/holder/credentials/{pres_ex_id}", response_model=PresentationCredentialsResponse)
async def fetch_holder_credentials(pres_ex_id: str, redis: Redis = Depends(get_redis)):
    return await fetch_presentation_credentials(redis, pres_ex_id)

@router.post("/holder/send-presentation", response_model=SendPresentationResponse)
async def send_holder_presentation(request: SendPresentationRequest, redis: Redis = Depends(get_redis)):
    return await send_presentation(redis, request)