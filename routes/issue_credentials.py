from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
import logging

import httpx
from pydantic import BaseModel, Field, ValidationError
from services.issue_credentials import (
    send_credential_proposal, 
    fetch_cred_ex_record,
    send_credential,
    SendCredentialRequest, SendCredentialResponse,
    fetch_cred_ex_id_list,
    delete_cred_ex_record,
    delete_all_cred_ex_records,
    CredentialProposalRequest
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/send_credential",
    summary="Issue Credential",
    description="Send a credential to the holder agent.",
    response_model=SendCredentialResponse
)
async def issue_credential(request: SendCredentialRequest):
    return await send_credential(request)

@router.get(
    "/fetch_cred_ex_id_list",
    summary="Fetch Credential Exchange ID List",
    description="Fetch the list of credential exchange IDs."
)
async def fetch_credential_exchange_id_list():
    return await fetch_cred_ex_id_list()

@router.delete(
    "/delete_cred_ex_record/{cred_ex_id}",
    summary="Delete Credential Exchange Record",
    description="Delete a credential exchange record by its ID."
)
async def delete_credential_exchange_record(cred_ex_id: str):
    try:
        result = await delete_cred_ex_record(cred_ex_id)
        return {"status": "Record deleted", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting credential exchange record {cred_ex_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.delete(
    "/delete_all_cred_ex_records",
    summary="Delete All Credential Exchange Records",
    description="Delete all credential exchange records."
)
async def delete_all_credential_exchange_records():
    try:
        result = await delete_all_cred_ex_records()
        return {"status": "All records deleted", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting all credential exchange records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post(
    "/proposal",
    summary="Send Credential Proposal",
    description="Send a credential proposal to the holder agent."
)
async def issue_credential_proposal(data: CredentialProposalRequest):
    try:
        # Log the incoming request for debugging
        logger.debug(f"Received credential proposal request: {data.dict(by_alias=True)}")
        # Construct proposal from request data
        proposal = {
            "comment": data.comment,
            "connection_id": data.connection_id,
            "credential_preview": data.credential_preview.dict(by_alias=True),
            "filter": data.filter.dict(),
            "auto_remove": data.auto_remove
        }

        result = await send_credential_proposal(proposal)
        logger.info(f"Credential proposal sent for cred_def_id {data.filter.indy.cred_def_id}")
        return {"status": "Proposal sent", "result": result}
    except ValidationError as e:
        logger.error(f"Validation error in /issue-credentials/proposal: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in /issue-credentials/proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get(
    "/fetch_record/{agent}/{cred_ex_id}",
    summary="Fetch Credential Exchange Record",
    description="Fetch the credential exchange record by its ID and agent name (issuer/holder/verifier)."
)
async def fetch_credential_exchange_record(agent: str, cred_ex_id: str):
    try:
        record = await fetch_cred_ex_record(agent, cred_ex_id)
        if not record:
            raise HTTPException(status_code=404, detail="Credential exchange record not found")
        return record
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching credential exchange record {cred_ex_id} from {agent.upper()}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e