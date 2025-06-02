from locust import HttpUser, task, between
import json
import time

class PresentationRequestUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        # Hardcoded connection_id
        self.connection_id = "1a38b3c6-9c0d3-40fc-95ed-b6b3b495d1a3"

    def poll_presentation_status(self, thread_id, max_retries=10, delay=1.0):
        """Poll presentation verification status."""
        for i in range(max_retries):
            with self.client.get(f"/presentations/verify/{thread_id}", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    if status == "verified":
                        response.success()
                        return True
                    elif status == "failed":
                        response.failure(f"Presentation verification failed: {data.get('error', 'Unknown error')}")
                        return False
                elif response.status_code == 425:
                    if i == max_retries - 1:
                        response.failure("Verification timeout")
                        return False
                    time.sleep(delay)
                    continue
                else:
                    response.failure(f"Failed to fetch verification status: {response.text}")
                    return False
        return False  # Timeout

    @task
    def send_presentation_request(self):
        payload = {}  # Empty, as endpoint hardcodes the request

        with self.client.post("/presentations/send-request", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                thread_id = data.get("thread_id")
                if not thread_id:
                    response.failure("Missing thread_id in response")
                    return

                # Poll for verification
                success = self.poll_presentation_status(thread_id)
                if not success:
                    self.environment.events.request_failure.fire(
                        request_type="POLL",
                        name="poll_presentation_status",
                        response_time=0,
                        exception=Exception("Presentation verification not completed in time.")
                    )
            else:
                response.failure(f"Failed to send presentation request: {response.text}")