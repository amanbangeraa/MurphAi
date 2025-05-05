import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import pvporcupine
from pvrecorder import PvRecorder
import tempfile
import os
import random
import time
from dotenv import load_dotenv 
from Backend.voice import generate_tts
from Backend.memory import init_db, get_answer, memory_agent
from Backend.sitesearch import site_open
from Backend.realtimesearch import realtime_search
import webbrowser

# Load environment variables
load_dotenv()
init_db()

api_key = os.getenv("GROQ_API_KEY")
access_key = os.getenv("ACCESS_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
if not access_key:
    raise ValueError("ACCESS_KEY environment variable is not set.")

SITE_COMMANDS = {
    "open youtube": "https://youtube.com",
    "open google": "https://google.com",
    "open wikipedia": "https://wikipedia.org",
    "open github": "https://github.com",
    "open spotify": "https://open.spotify.com/",
    "open amazon": "https://amazon.com",
    "open chatgpt": "https://chatgpt.com",
    "open gmail": "https://mail.google.com",
    "open whatsapp": "https://web.whatsapp.com",
    "open twitter": "https://twitter.com",
    "open linkedin": "https://linkedin.com",
    "open facebook": "https://facebook.com",
    "open instagram": "https://instagram.com",
    "open reddit": "https://reddit.com",
    "open netflix": "https://netflix.com",
}

# Track the last opened site
last_opened_site = None

def youtube_search(query):
    """Perform a YouTube search and open the results."""
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    site_open("youtube")
    webbrowser.open(search_url)
    return f"Searching YouTube for: {query}"

def brain(command):
    global last_opened_site
    lower_command = command.lower()
    
    # Check if it's a website command
    for phrase, url in SITE_COMMANDS.items():
        if phrase in lower_command:
            site_name = phrase.split()[-1].title()
            site_open(site_name)
            last_opened_site = site_name.lower()
            return f"Opening {site_name} for you!"
    
    # Check for YouTube search command
    if "search youtube for" in lower_command or "search on youtube for" in lower_command:
        search_query = lower_command.replace("search youtube for", "").replace("search on youtube for", "").strip()
        return youtube_search(search_query)
    
    # Check for simple search command when YouTube is the last opened site
    if last_opened_site == "youtube" and "search for" in lower_command:
        search_query = lower_command.replace("search for", "").strip()
        return youtube_search(search_query)
    
    # Check memory agent for past interactions
    memory_response = memory_agent(command)
    if memory_response:
        return memory_response
    
    # Check if real-time data is needed
    response = realtime_search(command)
    if response:
        return response
    
    # Otherwise, default AI response
    return get_answer(command)

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

def main():
    print("🔹 AI Assistant Ready")
    
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=["Backend/hey-Murph_en_linux_v3_0_0/hey-Murph_en_linux_v3_0_0.ppn"]
    )
    
    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
    
    try:
        recorder.start()
        print("🎧 Say 'Hey Murph' to activate...")
        active = False
        
        while True:
            pcm = recorder.read()
            pcm_array = np.array(pcm, dtype=np.int16)
            
            if not active and porcupine.process(pcm_array) >= 0:
                generate_tts(random.choice(["Yoo!", "Hey!", "What's up!"]))
                print("\n🚀 How can I help you?")
                active = True  
                start_time = time.time()
            
            if active:
                if time.time() - start_time > 7:
                    print("💤 No response detected. Deactivating...")
                    active = False
                    continue
                
                audio_path = record_audio()
                command = transcribe_audio(audio_path)
                print(f"👤 You said: {command}")
                
                response = brain(command)
                print(f"🤖 Response: {response}")
                generate_tts(response)
                
                active = False
    
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
    finally:
        porcupine.delete()
        recorder.stop()

if __name__ == "__main__":
    main()
