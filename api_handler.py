import json
import requests

class APIHandler:
    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def submit_data(self, url_path, data):
        """Submit the question data to the API."""
        try:
            response = requests.post(f"{self.base_url}/{url_path}", params=self.params, json=data)
            response.raise_for_status()
            print(f"Submission successful.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error submitting data: {e}")
            return False
