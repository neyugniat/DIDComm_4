from locust import HttpUser, task, between
import json
import time

class JwtSignVpUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task
    def sign_vp_jwt(self):
        holder_did = "did:key:z6Mkhvt86c35akmwbzvYf9uLWkwoeRjYf7ZTZk7yUpgwW96x"
        verkey = "4Ud5WMneFDHUVW5qyawVffPoprThFEK6sjD3eYivavKa"
        vc_jwt = "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFZERTQSIsICJraWQiOiAiZGlkOnNvdjpCQVNTZnRhWUsyYVp0SFJXSG44RThlI2tleS0xIn0.eyJpc3MiOiAiZGlkOnNvdjpCQVNTZnRhWUsyYVp0SFJXSG44RThlIiwgInN1YiI6ICJkaWQ6a2V5Ono2TWtodnQ4NmMzNWFrbXdienZZZjl1TFdrd29lUmpZZjdaVFprN3lVcGd3Vzk2eCIsICJ2YyI6IHsiY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgInR5cGUiOiBbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwgIlVuaXZlcnNpdHlEZWdyZWVDcmVkZW50aWFsIl0sICJjcmVkZW50aWFsU3ViamVjdCI6IHsiaWQiOiAiZGlkOmtleTp6Nk1raHZ0ODZjMzVha213Ynp2WWY5dUxXa3dvZVJqWWY3WlRaazd5VXBnd1c5NngiLCAibmFtZSI6ICJOZ3V5XHUxZWM1biBUXHUwMGUwaSBOZ3V5XHUwMGVhbiIsICJkZWdyZWUiOiAiQmFjaGVsb3Igb2YgSW5mb3JtYXRpb24gU2VjdXJpdHkiLCAic3RhdHVzIjogImdyYWR1YXRlZCIsICJncmFkdWF0aW9uRGF0ZSI6ICIyMDI1LTA3LTE2In19LCAiZXhwIjogMTc0ODQ5MDA2MSwgImlhdCI6IDE3NDg0ODY0NjF9.T50_ov6T6kQUsqHeunHFGfUn7bX6DR_E7mCcDx5iZKNqbC-3CrFXTR66i5rMuVH2_0MVOTpFbclEDhRnbLVeCQ"
        current_time = int(time.time())

        payload = {
            "did": holder_did,
            "payload": {
                "iss": holder_did,
                "aud": "did:sov:Q9eBByzvaHGgy22s5CeUPy",
                "vp": {
                    "@context": ["https://www.w3.org/2018/credentials/v1"],
                    "type": ["VerifiablePresentation"],
                    "verifiableCredential": [vc_jwt]
                },
                "exp": current_time + 60,
                "iat": current_time,
                "cnf": {}
            },
            "verkey": verkey
        }

        with self.client.post("/jwt-credentials/sign-vp-jwt", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                jwt = data.get("jwt")
                if not jwt:
                    response.failure("Missing jwt in response")
                else:
                    response.success()
            else:
                response.failure(f"Failed to sign VP-JWT: {response.text}")