from locust import HttpUser, task, between
import json
import time
import random
from datetime import datetime, date, timedelta

class JwtSignVcUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def random_name(self):
        """Generate a random Vietnamese name."""
        first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"]
        middle_names = ["Văn", "Thị", "Hữu", "Ngọc", "Minh"]
        last_names = ["Nguyên", "Hùng", "Dũng", "Linh", "Anh"]
        return f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}".strip()

    def random_date(self, start_year, end_year):
        """Generate a random date in YYYY-MM-DD."""
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = (end - start).days
        random_days = random.randint(0, delta)
        return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

    @task
    def sign_vc_jwt(self):
        issuer_did = "did:sov:BASSftaYK2aZtHRWHn8E8e"
        subject_did = "did:key:z6Mkk2eV94HFc3n1A7n1W6u4H1k3dY1yZ1z1z1z1z1z1z1z1"
        name = self.random_name()
        graduation_date = self.random_date(2023, 2026)
        current_time = int(time.time())

        payload = {
            "did": issuer_did,
            "payload": {
                "iss": issuer_did,
                "sub": subject_did,
                "vc": {
                    "@context": ["https://www.w3.org/2018/credentials/v1"],
                    "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                    "credentialSubject": {
                        "id": subject_did,
                        "name": name,
                        "degree": "Bachelor of Information Security",
                        "status": "graduated",
                        "graduationDate": graduation_date
                    }
                },
                "exp": current_time + 3600,
                "iat": current_time
            }
        }

        with self.client.post("/jwt-credentials/sign-vc-jwt", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                jwt = data.get("jwt")
                if not jwt:
                    response.failure("Missing jwt in response")
                else:
                    response.success()
            else:
                response.failure(f"Failed to sign VC-JWT: {response.text}")