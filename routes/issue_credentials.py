from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
import logging

import httpx
from pydantic import BaseModel, Field
from services.issue_credentials import (
    send_credential_proposal, 
    fetch_cred_ex_record,
    send_credential,
    SendCredentialRequest, SendCredentialResponse,
    fetch_cred_ex_id_list,
    delete_cred_ex_record,
    delete_all_cred_ex_records,
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




async def get_holder_connection_id_for_issuer():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:5000/connections/holder")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch connections from holder")
        connections = response.json().get("results", [])
        for conn in connections:
            if conn.get("their_label") == "ISSUER" and conn.get("state") == "active":
                return conn["connection_id"]
        raise HTTPException(status_code=404, detail="No active connection found with issuer")


class CredentialAttribute(BaseModel):
    name: str
    value: str

class CredentialPreview(BaseModel):
    type: str = Field("https://didcomm.org/issue-credential/2.0/credential-preview", alias="@type")
    attributes: List[CredentialAttribute]

class IndyFilter(BaseModel):
    cred_def_id: str

class Filter(BaseModel):
    indy: IndyFilter

class CredentialProposalRequest(BaseModel):
    comment: Optional[str] = "Requesting credential issuance"
    connection_id: str
    credential_preview: CredentialPreview
    filter: Filter
    auto_remove: bool = False

@router.post(
    "/proposal",
    summary="Send Credential Proposal",
    description="Send a credential proposal to the holder agent."
)
async def issue_credential_proposal(data: CredentialProposalRequest):
    try:
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
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in /issue-credentials/proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# @router.post(
#     "/proposal",
#     summary="Send Credential Proposal",
#     description="Send a credential proposal to the holder agent."
# )
# async def issue_credential_proposal(data: Dict[str, Any]):
#     try:
#         schema_id = data.get("schemaId")
#         cred_def_id = data.get("credDefId")
#         attributes = data.get("attributes", [])
#         if not schema_id or not cred_def_id or not attributes:
#             raise HTTPException(status_code=400, detail="Missing schemaId, credDefId, or attributes")

#         # Dynamically fetch the connection_id for the issuer
#         connection_id = await get_holder_connection_id_for_issuer()

#         proposal = {
#             "comment": "Requesting credential issuance",
#             "connection_id": connection_id,
#             "credential_preview": {
#                 "@type": "https://didcomm.org/issue-credential/2.0/credential-preview",
#                 "attributes": [{"name": attr["name"], "value": attr["value"]} for attr in attributes]
#             },
#             "filter": {
#                 "indy": {
#                     "cred_def_id": cred_def_id
#                 }
#             },
#             "auto_remove": False,
#         }

#         result = await send_credential_proposal(proposal)
#         logger.info(f"Credential proposal sent for schema {schema_id} and cred_def {cred_def_id}")
#         return {"status": "Proposal sent", "result": result}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error in /issue-credentials/proposal: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e)) from e

    
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
