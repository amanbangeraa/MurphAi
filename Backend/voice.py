import requests
import json
import io
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv 
import os

# Load environment variables from .env file
load_dotenv()

def generate_tts(text):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        play(audio)
    else:
        print(f"Error: {response.status_code}, {response.text}")
