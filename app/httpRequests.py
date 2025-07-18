import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

HOST = os.getenv("WEB_SERVER_HOST")
PORT = os.getenv("WEB_SERVER_PORT")
KEY = os.getenv("WEB_SERVER_AUTH_KEY")
    
def postWebServerData(data):
    if not all([HOST, PORT, KEY]):
        raise ValueError("Missing required environment variables: HOST, PORT, or AUTH_KEY")
    
    while True:
        try:
            url = f"http://{HOST}:{PORT}/api/saveText"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{KEY}"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()  # Raises an HTTPError if the response status is not 200
            print(f"Response: {response.text}")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            print("Retrying in 1 minute...")
            time.sleep(60)  # Wait for 1 minute before retrying

def main():
    data = {
        "text": "Text 2",
        "start_time": "2025-01-28 18:50:33.943169-02:00",
        "end_time": "2025-01-28 19:50:33.943169-02:00",
        "speaker": "2"
    }
    postWebServerData(data)

if __name__ == "__main__":
    main()
