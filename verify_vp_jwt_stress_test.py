from locust import HttpUser, task, between
import json

class GetBookListUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_book_list(self):
        payload = {
            "jwt": "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFZERTQSIsICJraWQiOiAiZGlkOmtleTp6Nk1raHZ0ODZjMzVha213Ynp2WWY5dUxXa3dvZVJqWWY3WlRaazd5VXBnd1c5NngjejZNa2h2dDg2YzM1YWttd2J6dllmOXVMV2t3b2VSallmN1pUWms3eVVwZ3dXOTZ4In0.eyJpc3MiOiAiZGlkOmtleTp6Nk1raHZ0ODZjMzVha213Ynp2WWY5dUxXa3dvZVJqWWY3WlRaazd5VXBnd1c5NngiLCAiYXVkIjogImRpZDpzb3Y6UTllQkJ5enZhSEdneTIyczVDZVVQeSIsICJ2cCI6IHsiY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgInR5cGUiOiBbIlZlcmlmaWFibGVQcmVzZW50YXRpb24iXSwgInZlcmlmaWFibGVDcmVkZW50aWFsIjogWyJleUowZVhBaU9pQWlTbGRVSWl3Z0ltRnNaeUk2SUNKRlpFUlRRU0lzSUNKcmFXUWlPaUFpWkdsa09uTnZkanBDUVZOVFpuUmhXVXN5WVZwMFNGSlhTRzQ0UlRobEkydGxlUzB4SW4wLmV5SnBjM01pT2lBaVpHbGtPbk52ZGpwQ1FWTlRablJoV1VzeVlWcDBTRkpYU0c0NFJUaGxJaXdnSW5OMVlpSTZJQ0prYVdRNmEyVjVPbm8yVFd0b2RuUTRObU16TldGcmJYZGllblpaWmpsMVRGZHJkMjlsVW1wWlpqZGFWRnByTjNsVmNHZDNWemsyZUNJc0lDSjJZeUk2SUhzaVkyOXVkR1Y0ZENJNklGc2lhSFIwY0hNNkx5OTNkM2N1ZHpNdWIzSm5Mekl3TVRndlkzSmxaR1Z1ZEdsaGJITXZkakVpWFN3Z0luUjVjR1VpT2lCYklsWmxjbWxtYVdGaWJHVkRjbVZrWlc1MGFXRnNJaXdnSWxWdWFYWmxjbk5wZEhsRVpXZHlaV1ZEY21Wa1pXNTBhV0ZzSWwwc0lDSmpjbVZrWlc1MGFXRnNVM1ZpYW1WamRDSTZJSHNpYVdRaU9pQWlaR2xrT210bGVUcDZOazFyYUhaME9EWmpNelZoYTIxM1lucDJXV1k1ZFV4WGEzZHZaVkpxV1dZM1dsUmFhemQ1VlhCbmQxYzVObmdpTENBaWJtRnRaU0k2SUNKT1ozVjVYSFV4WldNMWJpQlVYSFV3TUdVd2FTQk9aM1Y1WEhVd01HVmhiaUlzSUNKa1pXZHlaV1VpT2lBaVFtRmphR1ZzYjNJZ2IyWWdTVzVtYjNKdFlYUnBiMjRnVTJWamRYSnBkSGtpTENBaWMzUmhkSFZ6SWpvZ0ltZHlZV1IxWVhSbFpDSXNJQ0puY21Ga2RXRjBhVzl1UkdGMFpTSTZJQ0l5TURJMUxUQTNMVEUySW4xOUxDQWlaWGh3SWpvZ01UYzBPRFE1TURBMk1Td2dJbWxoZENJNklERTNORGcwT0RZME5qRjkuVDUwX292NlQ2a1FVc3FIZXVuSEZHZlVuN2JYNkRSX0U3bUNjRHg1aVpLTnFiQy0zQ3JGWFRSNjZpNXJNdVZIMl8wTVZPVHBGYmNsRURoUm5iTFZlQ1EiXX0sICJleHAiOiAxNzQ4Njc0ODE1LCAiaWF0IjogMTc0ODY3MTIxNSwgImNuZiI6IHsiandrIjogeyJrdHkiOiAiT0tQIiwgImNydiI6ICJFZDI1NTE5IiwgIngiOiAiNFVkNVdNbmVGREhVVlc1cXlhd1ZmZlBvcHJUaEZFSzZzakQzZVlpdmF2S2EifX19.z1Rurv4u4x7T1Wf-mobDSMvoa_mzsQi_elcNsiAc-WE0IRppQj9MEPAlBA9FeFZKV05tV8TC4vQTfcrl0XxzAg"
        }

        with self.client.post("/api/get-book-list", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if not isinstance(data, list) or not all("id" in book and "title" in book and "author" in book for book in data):
                    response.failure("Invalid book list response")
                else:
                    response.success()
            else:
                response.failure(f"Failed to get book list: {response.text}")