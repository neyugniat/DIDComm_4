import httpx

def get_connection_id():
    return "1a38b3c6-9c0d-40fc-95ed-b6b3495aaf1a"

async def send_presentation_request(verifier_url: str):
    connection_id = get_connection_id()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{verifier_url}/present-proof-2.0/send-request",
            json={
                "connection_id": connection_id,
                "presentation_request": {
                    "indy": {
                        "name": "Proof of Name",
                        "version": "1.0",
                        "requested_attributes": {"name_attr": {"name": "name"}},
                        "requested_predicates": {},
                        "non_revoked": {"from": 0, "to": 1744981040}
                    }
                }
            }
        )
    data = response.json()
    if response.status_code != 200 or "pres_ex_id" not in data:
        raise RuntimeError(f"Presentation request failed: {response.text}")
    return data["pres_ex_id"]

async def fetch_credentials(verifier_url: str, pres_ex_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{verifier_url}/present-proof-2.0/records/{pres_ex_id}/credentials"
        )
    data = response.json()
    if response.status_code != 200 or not isinstance(data, list):
        raise RuntimeError(f"Failed to fetch credentials: {response.text}")
    return data 