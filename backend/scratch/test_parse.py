import requests
import json

def test_voice_parse():
    url = "http://127.0.0.1:8000/api/v1/voice/parse"
    payload = {
        "transcript": "My name is Rahul and my phone number is 9876543210"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer demo_token"
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_voice_parse()
