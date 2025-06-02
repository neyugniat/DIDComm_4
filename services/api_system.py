from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
from typing import List, Optional
from services.jwt_credentials import VerifyJwtRequest, VerifyJwtResponse, verify_jwt
import logging, time

logger = logging.getLogger(__name__)

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str

class PatientRecord(BaseModel):
    id: int
    patient_name: str
    date_of_birth: str
    diagnosis: str
    last_visit: str

# Request model for JWT
class JwtRequest(BaseModel):
    jwt: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if any(error["loc"] == ["body", "jwt"] and error["type"] == "value_error.missing" for error in errors):
        return JSONResponse(
            status_code=422,
            content={"detail": "This API requires a VP-JWT in the request body."}
        )
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

async def get_verifier_did():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:5000/did/verifier")
            response.raise_for_status()
            did = response.json().get("did")
            if not did:
                raise HTTPException(404, "Verifier DID not found")
            return f"did:sov:{did}"
        except httpx.HTTPStatusError as e:
            raise HTTPException(500, f"Failed to fetch Verifier DID: {e.response.status_code}")

async def get_issuer_did():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:5000/did/issuer")
            response.raise_for_status()
            did = response.json().get("did")
            if not did:
                raise HTTPException(404, "Issuer DID not found")
            return f"did:sov:{did}"
        except httpx.HTTPStatusError as e:
            raise HTTPException(500, f"Failed to fetch Issuer DID: {e.response.status_code}")

async def verify_credentials(jwt: str, required_credential_type: Optional[str] = None):
    # Step 1: Verify JWT
    try:
        verification = await verify_jwt(VerifyJwtRequest(jwt=jwt))
    except HTTPException as e:
        logger.error(f"Error verifying JWT: {e.status_code}: {e.detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying JWT: {e.status_code}: {e.detail}"
        )

    if not verification.valid:
        logger.error("Invalid JWT provided")
        raise HTTPException(status_code=401, detail="Invalid JWT")

    # Step 2: Check audience matches expected Verifier DID
    expected_audience = await get_verifier_did()
    if verification.payload.get("aud") != expected_audience:
        logger.error(f"Invalid audience: expected {expected_audience}, got {verification.payload.get('aud')}")
        raise HTTPException(status_code=401, detail="Invalid audience")

    # Step 3: Check expiration
    exp = verification.payload.get("exp")
    if exp and exp < int(time.time()):
        logger.error("JWT is in the past")
        raise HTTPException(status_code=401, detail="JWT is in the past")

    # Step 4: Extract and verify embedded VC-JWTs
    vc_jwt = verification.payload.get("vp", {}).get("verifiableCredential", [None])[0]
    if not vc_jwt:
        logger.error("No VC-JWT in VP")
        raise HTTPException(status_code=400, detail="No VC-JWT in VP")

    try:
        vc_verification = await verify_jwt(VerifyJwtRequest(jwt=vc_jwt))
    except HTTPException as e:
        logger.error(f"Error verifying VC-JWT: {e.status_code}: {e.detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying VC-JWT: {e.status_code}: {e.detail}"
        )

    if not vc_verification.valid:
        logger.error("Invalid VC-JWT")
        raise HTTPException(status_code=401, detail="Invalid VC-JWT")

    # Step 5: Validate issuer DID of VC-JWT
    expected_issuer = await get_issuer_did()
    if vc_verification.payload.get("iss") != expected_issuer:
        logger.error(f"Invalid issuer: expected {expected_issuer}, got {vc_verification.payload.get('iss')}")
        raise HTTPException(status_code=401, detail="Invalid issuer")

    # Step 6: Validate that sub == vc.credentialSubject.id
    sub = vc_verification.payload.get("sub")
    credential_subject_id = vc_verification.payload.get("vc", {}).get("credentialSubject", {}).get("id")
    if sub != credential_subject_id:
        logger.error("VC subject does not match credentialSubject.id")
        raise HTTPException(status_code=401, detail="Subject mismatch")

    # Step 7: Validate credential type
    if required_credential_type:
        vc_types = vc_verification.payload.get("vc", {}).get("type", [])
        if required_credential_type not in vc_types:
            logger.error(f"Invalid credential type: expected {required_credential_type}, got {vc_types}")
            raise HTTPException(status_code=403, detail=f"This endpoint requires a {required_credential_type} credential")

    # Step 8: Validate required attributes based on credential type
    credential_subject = vc_verification.payload.get("vc", {}).get("credentialSubject", {})
    if required_credential_type == "DoctorCredential":
        required_fields = ["ho_ten", "chuyen_khoa", "licenseNumber"]
        missing_fields = [field for field in required_fields if not credential_subject.get(field)]
        if missing_fields:
            logger.error(f"Missing required fields in DoctorCredential: {missing_fields}")
            raise HTTPException(
                status_code=403,
                detail=f"DoctorCredential missing required fields: {', '.join(missing_fields)}"
            )
    elif required_credential_type == "UniversityDegreeCredential":
        required_fields = ["name", "degree"]
        missing_fields = [field for field in required_fields if not credential_subject.get(field)]
        if missing_fields:
            logger.error(f"Missing required fields in UniversityDegreeCredential: {missing_fields}")
            raise HTTPException(
                status_code=403,
                detail=f"UniversityDegreeCredential missing required fields: {', '.join(missing_fields)}"
            )

    return verification, vc_verification

@app.post("/get-book-list", response_model=List[Book])
async def get_book_list(request: JwtRequest) -> List[Book]:
    try:
        # Verify credentials, require UniversityDegreeCredential
        await verify_credentials(request.jwt, required_credential_type="UniversityDegreeCredential")

        # Return mock book list
        books = [
            Book(id=1, title="To Kill a Mockingbird", author="Harper Lee"),
            Book(id=2, title="1984", author="George Orwell"),
            Book(id=3, title="Pride and Prejudice", author="Jane Austen"),
            Book(id=4, title="The Great Gatsby", author="F. Scott Fitzgerald"),
            Book(id=5, title="The Catcher in the Rye", author="J.D. Salinger"),
            Book(id=6, title="Lord of the Rings", author="J.R.R. Tolkien"),
            Book(id=7, title="Harry Potter and the Sorcerer's Stone", author="J.K. Rowling"),
            Book(id=8, title="The Hobbit", author="J.R.R. Tolkien"),
            Book(id=9, title="Fahrenheit 451", author="Ray Bradbury"),
            Book(id=10, title="Jane Eyre", author="Charlotte Brontë"),
            Book(id=11, title="Animal Farm", author="George Orwell"),
            Book(id=12, title="The Alchemist", author="Paulo Coelho"),
            Book(id=13, title="Brave New World", author="Aldous Huxley"),
            Book(id=14, title="The Road", author="Cormac McCarthy"),
            Book(id=15, title="Moby-Dick", author="Herman Melville"),
            Book(id=16, title="Wuthering Heights", author="Emily Brontë"),
            Book(id=17, title="The Odyssey", author="Homer"),
            Book(id=18, title="Catch-22", author="Joseph Heller"),
            Book(id=19, title="Dune", author="Frank Herbert"),
            Book(id=20, title="The Grapes of Wrath", author="John Steinbeck")
        ]

        return books

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Unhandled error in get_book_list")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/get-patient-records", response_model=List[PatientRecord])
async def get_patient_records(request: JwtRequest) -> List[PatientRecord]:
    try:
        # Verify credentials, require DoctorCredential
        await verify_credentials(request.jwt, required_credential_type="DoctorCredential")

        # Return mock patient records
        patient_records = [
            PatientRecord(
                id=1,
                patient_name="John Doe",
                date_of_birth="1975-03-15",
                diagnosis="Hypertension",
                last_visit="2025-04-10"
            ),
            PatientRecord(
                id=2,
                patient_name="Jane Smith",
                date_of_birth="1982-07-22",
                diagnosis="Type 2 Diabetes",
                last_visit="2025-05-01"
            ),
            PatientRecord(
                id=3,
                patient_name="Alice Johnson",
                date_of_birth="1990-11-30",
                diagnosis="Asthma",
                last_visit="2025-03-20"
            ),
            PatientRecord(
                id=4,
                patient_name="Bob Brown",
                date_of_birth="1965-09-05",
                diagnosis="Chronic Back Pain",
                last_visit="2025-04-25"
            ),
            PatientRecord(
                id=5,
                patient_name="Carol White",
                date_of_birth="1978-01-12",
                diagnosis="Migraine",
                last_visit="2025-05-15"
            )
        ]

        return patient_records

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Unhandled error in get_patient_records")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")