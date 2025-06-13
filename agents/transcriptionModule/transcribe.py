import requests
import os
from pathlib import Path

SYSTEM_PROMPT = """
You are a transcribing assistant, take the audio submitted by the user and transcribe it as text as-is.
Do not translate, do not add anything, just transcribe. If the audio is empty just answer with an empty message.
If the audio is missing, just answer with an empty message.
"""

def chat_with_audio(audio_file_path, api_url="http://192.168.0.122:9091/v1/chat/completions"):
    """Send audio to ChatCompletion endpoint."""
    
    if not Path(audio_file_path).is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    with open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()
        
    # Base64 encode audio if required by your API
    import base64
    audio_b64 = base64.b64encode(audio_content).decode('utf-8')
    
    payload = {
        "samplers": "edkypmxt",
        "temperature": 0.8,
        "dynatemp_range": 0,
        "dynatemp_exponent": 1,
        "top_k": 40,
        "top_p": 0.95,
        "min_p": 0.05,
        "typical_p": 1,
        "xtc_probability": 0,
        "xtc_threshold": 0.1,
        "repeat_last_n": 64,
        "repeat_penalty": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "dry_multiplier": 0,
        "dry_base": 1.75,
        "dry_allowed_length": 2,
        "dry_penalty_last_n": -1,
        "max_tokens": -1,
        "messages": [
            {
                "content": [
                    {
                        "input_audio": {"data": audio_b64, "format": "mp3"},
                        "type": "input_audio"
                    },
                    {
                        "text": SYSTEM_PROMPT,
                        "type": "text"
                    },
                ],
                "role": "user"
            }
        ]
    }
    print(payload)
    
    response = requests.post(api_url, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    return response.json()

print(chat_with_audio("./recording_ner_romain_1.mp3"))