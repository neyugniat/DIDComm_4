from fastapi import HTTPException
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional, Union
import httpx
import logging
import base64
from config import settings

logger = logging.getLogger(__name__)

# Pydantic models for create_did
class CreateDidOptions(BaseModel):
    key_type: str = "ed25519"

class CreateDidRequest(BaseModel):
    method: str = "key"
    options: CreateDidOptions

class CreateDidResult(BaseModel):
    did: str
    verkey: str
    posture: str
    key_type: str
    method: str
    metadata: Dict[str, Any]

class CreateDidResponse(BaseModel):
    result: CreateDidResult

# Pydantic models for sign_vc_jwt
class UniversityDegreeCredentialSubject(BaseModel):
    id: str
    name: str
    degree: str
    status: str
    graduationDate: str

class DoctorCredentialSubject(BaseModel):
    id: str
    ho_ten: str
    chuc_vu: str
    chuyen_khoa: str
    benh_vien: str
    licenseNumber: str

class VerifiableCredential(BaseModel):
    context: List[str] = ["https://www.w3.org/2018/credentials/v1"]
    type: List[str]
    credentialSubject: Union[UniversityDegreeCredentialSubject, DoctorCredentialSubject]

    @validator('type')
    def validate_credential_type(cls, v):
        if "VerifiableCredential" not in v:
            raise ValueError("Type must include 'VerifiableCredential'")
        return v

class SignVcJwtPayload(BaseModel):
    iss: str
    sub: str
    vc: VerifiableCredential
    exp: int
    iat: int

class SignVcJwtRequest(BaseModel):
    did: str
    payload: SignVcJwtPayload

class SignVcJwtResponse(BaseModel):
    jwt: str

# Pydantic models for sign_vp_jwt
class VerifiablePresentation(BaseModel):
    context: List[str] = ["https://www.w3.org/2018/credentials/v1"]
    type: List[str] = ["VerifiablePresentation"]
    verifiableCredential: List[str]

class Jwk(BaseModel):
    kty: str
    crv: str
    x: str

class Cnf(BaseModel):
    jwk: Optional[Jwk] = None

class SignVpJwtPayload(BaseModel):
    iss: str
    aud: str
    vp: VerifiablePresentation
    exp: int
    iat: int
    cnf: Cnf

class SignVpJwtRequest(BaseModel):
    did: str
    payload: SignVpJwtPayload
    verkey: str 

class SignVpJwtResponse(BaseModel):
    jwt: str

# Pydantic models for verify_jwt
class VerifyJwtHeaders(BaseModel):
    typ: str
    alg: str
    kid: str
    
class VerifyJwtRequest(BaseModel):
    jwt: str

class VerifyJwtResponse(BaseModel):
    valid: bool
    headers: VerifyJwtHeaders
    payload: Dict[str, Any]
    kid: str

async def create_did(request: CreateDidRequest) -> CreateDidResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.HOLDER_AGENT_URL}/wallet/did/create",
                json=request.dict(),
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to create DID: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to create DID: {response.text}")
            result = response.json()
            logger.info(f"Created DID: {result}")
            return CreateDidResponse(**result)
    except Exception as e:
        logger.error(f"Error creating DID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating DID: {str(e)}")

async def sign_vc_jwt(request: SignVcJwtRequest) -> SignVcJwtResponse:
    logger.info(f"SignVcJwtRequest: {request}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ISSUER_AGENT_URL}/wallet/jwt/sign",
                json=request.dict(),
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to sign VC-JWT: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to sign VC-JWT: {response.text}")
            jwt_token = response.text.strip('"')
            logger.info(f"Signed VC-JWT: {jwt_token[:50]}...")
            return SignVcJwtResponse(jwt=jwt_token)
    except Exception as e:
        logger.error(f"Error signing VC-JWT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error signing VC-JWT: {str(e)}")

async def sign_vp_jwt(request: SignVpJwtRequest) -> SignVpJwtResponse:
    try:
        # Convert verkey to JWK format
        verkey_bytes = base64.b64decode(request.verkey)
        
        x_value = base64.urlsafe_b64encode(verkey_bytes).decode('utf-8').rstrip('=')
        request.payload.cnf = Cnf(
            jwk=Jwk(
                kty="OKP",
                crv="Ed25519",
                x=x_value
            )
        )
        
        logger.info(f"Signing VP-JWT with DID: {request.did} and verkey: {request.verkey}")
        logger.debug(f"VP-JWT payload: {request.payload.json()}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.HOLDER_AGENT_URL}/wallet/jwt/sign",
                json=request.dict(),
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to sign VP-JWT: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to sign VP-JWT: {response.text}")
            jwt_token = response.text.strip('"')
            logger.info(f"Signed VP-JWT: {jwt_token[:50]}...")
            return SignVpJwtResponse(jwt=jwt_token)
    except Exception as e:
        logger.error(f"Error signing VP-JWT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error signing VP-JWT: {str(e)}")

async def verify_jwt(request: VerifyJwtRequest) -> VerifyJwtResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.VERIFIER_AGENT_URL}/wallet/jwt/verify",
                json=request.dict(),
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to verify JWT: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to verify JWT: {response.text}")
            result = response.json()
            logger.info(f"Verified JWT: valid={result['valid']}")
            return VerifyJwtResponse(**result)
    except Exception as e:
        logger.error(f"Error verifying JWT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying JWT: {str(e)}")