import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import pvporcupine
from pvrecorder import PvRecorder
import tempfile
import os
import threading
from Backend.voice import generate_tts
from Backend.memory import init_db, get_answer, memory_agent
from dotenv import load_dotenv 
import random
import time
from Backend.sitesearch import site_open
import webbrowser
from flask import Flask, render_template
from flask_socketio import SocketIO

from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import socket
import webbrowser

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def run_server():
    socketio.run(app, port=5000)

def wait_for_server(host="localhost", port=5000, timeout=10):
    """Wait until the server is ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False

# ✅ Start server thread
threading.Thread(target=run_server, daemon=True).start()

threading.Thread(target=run_server).start()
time.sleep(1)  # wait for server to start

if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    webbrowser.get(using='firefox').open_new("http://localhost:5000")


# Load environment variables from .env file
load_dotenv()

# Initialize database
init_db()


# Set API Keys
api_key = os.getenv("GROQ_API_KEY")
access_key = os.getenv("PORCUPINE_ACCESS_KEY")


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
    "open chat gpt": "https://chatgpt.com",
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

def handle_website_commands(command):
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
    
    return None

def random_greet():
    greetings = ["uhhuhh!", "Yoo!", "Hey!", "Helloooo!", "Hoiii!", "What's up!", "Hey there!", "Hey, what's up?"]
    return random.choice(greetings)

def record_audio(duration=5, sample_rate=16000):
    print("🎙️ Listening...")
    
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.int16)
    #socketio.emit("user-speaking")
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
    site_response = handle_website_commands(command)
    if site_response:
        return site_response
    
    memory_response = memory_agent(command)
    if memory_response:
        return memory_response
    
    prompt = f"""
    You are an AI assistant with the following personality:
    {character_personality}

    The user has said:
    {command}

    Respond in a way that aligns with your personality.
    """
    
    response = get_answer(prompt)
    return response

def is_response_complete(response):
    return response.strip().endswith(('.', '!'))

def main():
    character_personality = load_character()
    print(f"🔹 Personality Loaded: {character_personality}")
    
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=["Backend/Hey-Murph_en_linux_v3_0_0/Hey-Murph_en_linux_v3_0_0.ppn"]
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
                generate_tts(random_greet())
                print("\n🚀 How can I help you?")
                active = True  
                start_time = time.time()
                socketio.emit("user-speaking")

            if active:
                if time.time() - start_time > 7:
                    print("💤 No response detected. Deactivating...")
                    active = False
                    socketio.emit("user-speaking-done")
                    continue

                audio_path = record_audio()
                command = transcribe_audio(audio_path)
                print(f"👤 You said: {command}")

                socketio.emit("user-speaking-done")
                socketio.emit("user-transcription", {"text": command})

                # Silence command
                if any(phrase in command.lower() for phrase in ["stop", "shut up", "mute"]):
                    generate_tts("Okay, going silent.")
                    print("🔇 Assistant silenced by user command.")
                    active = False
                    continue

                response = get_character_response(command, character_personality)
                print(f"🤖 Response: {response}")

                socketio.emit("ai-speaking")
                socketio.emit("ai-transcription", {"text": response})
                generate_tts(response)
                socketio.emit("ai-speaking-done")

                if is_response_complete(response):
                    print("💤 Deactivated")
                    active = False
                else:
                    print("🔄 Still Active...")
                    start_time = time.time()

    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
    finally:
        porcupine.delete()
        recorder.stop()

if __name__ == "__main__":
    main()
