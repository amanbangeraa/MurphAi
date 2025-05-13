import os
import wave
import json
import time
import pyaudio
import pvporcupine
import openai
import threading
from tools.tts import generate_tts
from tools.memory import write_to_memory
from tools.web_commands import execute_web_command
from tools.whisper import transcribe_audio
from tools.assistant import get_answer

WAKE_WORD = "hey murph"
AUDIO_PATH = "audio.wav"
CHARACTER_PATH = "character.txt"

# Load assistant personality
with open(CHARACTER_PATH, "r") as file:
    personality = file.read()

# Setup Porcupine wake-word engine
porcupine = pvporcupine.create(keywords=[WAKE_WORD])
pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

# Conversation history
conversation_history = []

def listen_for_wake_word():
    print("Listening for wake word...")
    while True:
        pcm = stream.read(porcupine.frame_length)
        pcm = list(pcm)
        if porcupine.process(pcm) >= 0:
            print("[Wake Word Detected]")
            record_and_respond()

def record_audio():
    print("Listening...")
    frames = []
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024
    )
    for _ in range(0, int(44100 / 1024 * 5)):  # Record 5 seconds
        data = stream.read(1024)
        frames.append(data)
    stream.stop_stream()
    stream.close()

    wf = wave.open(AUDIO_PATH, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b"".join(frames))
    wf.close()

def record_and_respond():
    while True:
        record_audio()
        text = transcribe_audio(AUDIO_PATH)
        print(f"You said: {text}")
        if not text:
            continue
        if "stop conversation" in text.lower():
            print("Stopping conversation loop.")
            break

        # Memory and history
        write_to_memory(text)
        conversation_history.append({"role": "user", "content": text})

        # Web commands (optional)
        if execute_web_command(text):
            continue

        # AI response
        response = get_answer(text, personality, conversation_history)
        print(f"Murph: {response}")
        conversation_history.append({"role": "assistant", "content": response})

        # Speak response
        generate_tts(response)

        print("Awaiting next input (say 'stop conversation' to exit)...")

if __name__ == "__main__":
    listen_for_wake_word()
