import requests
import os

API_BASE = os.getenv("API_BASE", "http://192.168.0.185:10000")

def embed_prompt(user_prompt: str) -> list[float]:
    response : requests.Response = requests.post(f"{API_BASE}/v1/get_embeddings", json={"queries": [user_prompt]})
    response.raise_for_status() # In case it fails !

    response_json : list[float] = response.json()["vectors"][0]


    # Enforce type of response_json
    assert isinstance(response_json, list), "response_json is not a list"
    assert all(isinstance(i, float) for i in response_json), "Not all elements in response_json are floats"
    
    return response_json

if __name__ == "__main__":
    embed_prompt("Hello, world!")