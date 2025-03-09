import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import pvporcupine
from pvrecorder import PvRecorder
import tempfile
import os
from Backend.voice import generate_tts
from Backend.memory import init_db, get_answer, memory_agent
from dotenv import load_dotenv 
import random
import time

# Load environment variables from .env file
load_dotenv()

# Initialize database
init_db()

# Set API Keys
api_key = os.getenv("GROQ_API_KEY")
access_key = os.getenv("ACCESS_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
if not access_key:
    raise ValueError("ACCESS_KEY environment variable is not set.")

def random_greet():
    greetings = ["uhhuhh!", "Yoo!", "Hey!", "Helloooo!", "Hoiii!", "What's up!", "Hey there!", "Hey, what's up?"]
    return random.choice(greetings)

def record_audio(duration=5, sample_rate=16000):
    print("🎙️ Listening...")
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav.write(temp_wav.name, sample_rate, audio_data)
    return temp_wav.name


def transcribe_audio(file_path):
    from groq import Groq
    client = Groq(api_key=api_key)
    
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
        )
    return transcription.text

def load_character():
    char_file = "Backend/character.txt"
    if os.path.exists(char_file):
        with open(char_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    return "I am your AI assistant."


def get_character_response(command, character_personality):
    """Generate a response that adheres to the character's personality."""
    # First, check if the memory agent has a response
    memory_response = memory_agent(command)
    if memory_response:
        return memory_response
    
    # If no relevant memory, generate a new response
    prompt = f"""
    You are an AI assistant with the following personality:
    {character_personality}

    The user has said:
    {command}

    Respond in a way that aligns with your personality.
    """
    
    # Use the get_answer function to generate the response
    response = get_answer(prompt)
    return response

def is_response_complete(response):
    """Check if the response ends with a sentence-ending punctuation."""
    return response.strip().endswith(('.', '!'))

def main():
    character_personality = load_character()
    print(f"🔹 Personality Loaded: {character_personality}")
    
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=["Backend/hey-Murph_en_linux_v3_0_0/hey-Murph_en_linux_v3_0_0.ppn"]
    )
    
    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
    
    try:
        recorder.start()
        print("🎧 Say 'Hey Murph' to activate...")
        
        active = False  # Track if the AI is in an active state
        
        while True:
            pcm = recorder.read()
            pcm_array = np.array(pcm, dtype=np.int16)
            
            # Check for activation keyword if not already active
            if not active and porcupine.process(pcm_array) >= 0:
                generate_tts(random_greet())
                print("\n🚀 How can I help you?")
                active = True  
                start_time = time.time()  # Start response timer
            
            # If active, listen for user input
            if active:
                # Check if the user is taking too long to respond (7 seconds timeout)
                if time.time() - start_time > 7:
                    print("💤 No response detected. Deactivating...")
                    active = False
                    continue  # Skip to next iteration
                
                audio_path = record_audio()
                command = transcribe_audio(audio_path)
                print(f"👤 You said: {command}")
                
                response = get_character_response(command, character_personality)
                print(f"🤖 Response: {response}")
                
                generate_tts(response)
                
                if is_response_complete(response):
                    print("💤 Deactivated")
                    active = False 
                else:
                    print("🔄 Still Active...")
                    start_time = time.time()  # Reset response timer

    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
    finally:
        porcupine.delete()
        recorder.stop()

if __name__ == "__main__":
    main()
