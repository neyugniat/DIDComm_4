from locust import HttpUser, task, between
import json
import time
import random

class CredentialProposalUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.connection_id = "f99bfc9f-6d64-4014-82f8-5d3b15bd05a3"
        self.cred_def_id = "BASSftaYK2aZtHRWHn8E8e:3:CL:26:default"
        self.schema_id = "BASSftaYK2aZtHRWHn8E8e:2:Transcript:1.0"

    def poll_proposal_status(self, cred_ex_id, max_retries=10, delay=1.0):
        for i in range(max_retries):
            with self.client.get(f"/issue-credentials/fetch_record/HOLDER/{cred_ex_id}", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    state = data.get("cred_ex_record", {}).get("state")
                    if state in ["proposal-sent", "offer-received"]:
                        response.success()
                        return True
                    else:
                        time.sleep(delay)
                else:
                    response.failure(f"Failed to fetch credential exchange record: {response.text}")
                    return False
        return False  # Timeout

    def random_name(self):
        """Generate a random Vietnamese name."""
        first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"]
        middle_names = ["Văn", "Thị", "Hữu", "Ngọc", "Minh"]
        last_names = ["Nguyên", "Hùng", "Dũng", "Linh", "Anh"]
        return f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}".strip()

    @task
    def send_proposal(self):
        payload = {
            "schemaId": self.schema_id,
            "credDefId": self.cred_def_id,
            "attributes": [
                {"name": "name", "value": self.random_name()}
            ]
        }

        with self.client.post("/issue-credentials/proposal", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                cred_ex_id = result.get("cred_ex_id")
                if not cred_ex_id:
                    response.failure("Missing cred_ex_id in response")
                    return

                # Poll for completion
                success = self.poll_proposal_status(cred_ex_id)
                if not success:
                    self.environment.events.request_failure.fire(
                        request_type="POLL",
                        name="poll_proposal_status",
                        response_time=0,
                        exception=Exception("Credential proposal not completed in time.")
                    )
            else:
                response.failure(f"Failed to send proposal: {response.text}")