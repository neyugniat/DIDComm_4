from fastapi import APIRouter, Depends
from typing import AsyncGenerator
from services.graduated_presentation import (
    SendProofRequest,
    SendProofResponse,
    SendPresentationRequest,
    SendPresentationResponse,
    send_proof_request,
    send_presentation
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
async def send_graduated_proof_request(request: SendProofRequest, redis: Redis = Depends(get_redis)):
    return await send_proof_request(redis, request)

@router.post("/holder/send-presentation", response_model=SendPresentationResponse)
async def send_graduated_presentation(request: SendPresentationRequest, redis: Redis = Depends(get_redis)):
    return await send_presentation(redis, request)