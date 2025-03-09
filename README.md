# Murph - AI Voice Assistant

Murph is a voice-activated AI assistant that listens for a wake word and responds in a personalized way based on a defined character personality. It uses **Whisper AI for transcription**, **Porcupine for wake word detection**, and **Groq for generating responses**.

---

## 🚀 Features
- **Wake Word Activation:** Listens for "Hey Murph" to activate.
- **Speech-to-Text:** Uses Whisper AI for high-quality transcription.
- **Character Personality:** Customizable responses based on predefined personality.
- **Memory Integration:** Stores and recalls past interactions.
- **Text-to-Speech (TTS):** Generates natural voice responses.
- **Timeout Detection:** Deactivates if no user response is detected.

---

## 📌 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/murph-ai.git
cd murph-ai
```

### 2️⃣ Install Dependencies
Make sure you have **Python 3.8+** installed.
```sh
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables
Create a **.env** file in the project root and add:
```env
GROQ_API_KEY=your_groq_api_key
ACCESS_KEY=your_porcupine_access_key
```

### 4️⃣ Run the Assistant
```sh
python main.py
```

---

## 🛠️ Configuration
### Character Personality
Edit `Backend/character.txt` to define your AI’s personality.

### Wake Word Model
Replace `hey-Murph_en_linux_v3_0_0.ppn` with your own Porcupine model for a custom wake word.

---

## 🖥️ Usage
1. Start the assistant (`python main.py`).
2. Say **"Hey Murph"** to activate.
3. Speak your command, and Murph will respond!

---

## 📚 Technologies Used
- **Python** 🐍
- **Whisper AI** (Speech Recognition)
- **Porcupine** (Wake Word Detection)
- **Groq API** (AI Response Generation)
- **Sounddevice & SciPy** (Audio Processing)

---

## 🤝 Contributing
Feel free to submit **issues** or **pull requests**!

---

## 📜 License
MIT License - Free to use and modify!

---

🔹 **Built by [Aman Bangera](https://github.com/amanbangeraa)** with ❤️

