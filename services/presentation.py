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
    return {
        "pres_ex_id": data["pres_ex_id"],
        "thread_id": data.get("thread_id", data["pres_ex_id"])  # Fallback to pres_ex_id if thread_id missing
    }

# async def fetch_credentials(holder_url: str, pres_ex_id: str):
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"{holder_url}/present-proof-2.0/records/{pres_ex_id}/credentials"
#         )
#     data = response.json()
#     if response.status_code != 200 or not isinstance(data, list):
#         raise RuntimeError(f"Failed to fetch credentials: {response.text}")
#     return data

async def fetch_credentials(holder_url: str, pres_ex_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{holder_url}/present-proof-2.0/records/{pres_ex_id}/credentials",
            headers={"Accept": "application/json"},
        )

    raw = response.text
    print(f"📝 [fetch_credentials] Raw response for {pres_ex_id} (Content-Type: {response.headers.get('content-type')}):\n{raw!r}")

    try:
        data = response.json()
    except Exception as e:
        print(f"❗ JSON decode error for {pres_ex_id}: {e}")
        lines = raw.splitlines()
        print(f"📄 Response split into {len(lines)} line(s):")
        for i, line in enumerate(lines, 1):
            print(f"  {i:02d}: {line!r}")
        raise

    if response.status_code != 200 or not isinstance(data, list):
        raise RuntimeError(f"Failed to fetch credentials: {response.status_code} / {data}")

    return data

async def send_presentation(holder_url, pres_ex_id: str, cred_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{holder_url}/present-proof-2.0/records/{pres_ex_id}/send-presentation",
            json={
                "indy": {
                    "requested_attributes": {
                        "name_attr": {
                            "cred_id": cred_id,
                            "revealed": True
                        }
                    },
                    "requested_predicates": {},
                    "self_attested_attributes": {}
                }
            }
        )
    if response.status_code != 200:
        raise RuntimeError(f"Failed to send presentation: {response.text}")
    return True