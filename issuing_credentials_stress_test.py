from locust import HttpUser, task, between
import json
import time
import random
from datetime import datetime, date, timedelta

class CredentialIssuanceUser(HttpUser):
    wait_time = between(1, 3) 

    def on_start(self):
        self.connection_id = "6b2828df-cc23-4c43-b775-47353dbdf875"

    def poll_credential_status(self, cred_ex_id, max_retries=10, delay=1.0):
        for i in range(max_retries):
            with self.client.get(f"/issue-credentials/fetch_record/ISSUER/{cred_ex_id}", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    state = data.get("cred_ex_record", {}).get("state")
                    if state == "done":
                        response.success()
                        return True
                    else:
                        time.sleep(delay)
                else:
                    response.failure("Failed to fetch credential exchange record")
                    return False
        return False  # Timeout

    def random_date(self, start_year, end_year):
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = (end - start).days
        random_days = random.randint(0, delta)
        return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

    def calculate_unix_dob(self, dob):
        epoch = date(1970, 1, 1)
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        return str((dob_date - epoch).days)

    def random_name(self):
        first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"]
        middle_names = ["Văn", "Thị", "Hữu", "Ngọc", "Minh"]
        last_names = ["Nguyên", "Hùng", "Dũng", "Linh", "Anh"]
        return f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}".strip()

    def random_student_id(self):
        year = random.randint(15, 24) 
        num = random.randint(1000, 9999)
        return f"AT{year}N{num:04d}"

    @task
    def issue_credential(self):
        name = self.random_name()
        date_of_birth = self.random_date(2000, 2010)
        unix_dob = self.calculate_unix_dob(date_of_birth)
        graduation_date = self.random_date(2023, 2026)
        gpa = str(random.randint(300, 400))  
        student_id = self.random_student_id()
        major = random.choice(["An toàn Thông tin", "Công nghệ Thông tin", "Kỹ thuật Phần mềm"])
        university = "Học viện Kỹ thuật Mật mã"

        payload = {
            "auto_remove": False,
            "comment": f"Issuing university degree to {name}",
            "connection_id": self.connection_id,
            "credential_preview": {
                "@type": "issue-credential/2.0/credential-preview",
                "attributes": [
                    {"name": "name", "value": name},
                    {"name": "dateOfBirth", "value": date_of_birth},
                    {"name": "graduationDate", "value": graduation_date},
                    {"name": "degree", "value": "Bằng cử nhân"},
                    {"name": "unixdob", "value": unix_dob},
                    {"name": "studentId", "value": student_id},
                    {"name": "university", "value": university},
                    {"name": "major", "value": major},
                    {"name": "gpa", "value": gpa},
                ],
            },
            "filter": {
                "indy": {
                    "cred_def_id": "BASSftaYK2aZtHRWHn8E8e:3:CL:50:support_revocation",
                    "issuer_did": "BASSftaYK2aZtHRWHn8E8e",
                    "schema_id": "BASSftaYK2aZtHRWHn8E8e:2:UniversityDegree:1.2",
                    "schema_issuer_did": "BASSftaYK2aZtHRWHn8E8e",
                    "schema_name": "UniversityDegree",
                    "schema_version": "1.2"
                }
            },
            "trace": False
        }

        with self.client.post("/issue-credentials/send_credential", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                cred_ex_id = data.get("cred_ex_id")
                if not cred_ex_id:
                    response.failure("Missing cred_ex_id in response")
                    return
                
                success = self.poll_credential_status(cred_ex_id)
                if not success:
                    self.environment.events.request_failure.fire(
                        request_type="POLL",
                        name="poll_credential_status",
                        response_time=0,
                        exception=Exception("Credential issuance not completed in time.")
                    )
            else:
                response.failure("Failed to issue credential")