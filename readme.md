 **Murph AI**

A voice-activated AI assistant inspired by TARS from *Interstellar* and built with a mix of vibe coding and cutting-edge tech. Murph listens, responds, remembers, and even performs automation tasks like opening apps. It integrates with advanced APIs to provide fast responses.

---

## **Features**

* 🎤 **Wake word detection** (Porcupine)
* 🧠 **Real-time transcription** (Whisper AI)
* ⚡ **Fast AI responses** using **Groq** LLM
* 🧬 **Memory** to remember past interactions
* 🖱️ **PC automation** to open apps or trigger actions
* Hand sign detection, dedicated hardware, and real-time internet integration coming soon!

---

## **Tech Stack**

* **Porcupine** – Wake word detection engine
* **Whisper AI** – Speech-to-text transcription
* **Groq** – Fast language model inference
* **Python** – Backend and scripting
* **Flask** – Web framework (optional, if you're using a web interface)

---

## **Getting Started**

### **Prerequisites**

Before running Murph AI on your local machine, make sure you have the following installed:

1. **Python 3.x**
   Download and install Python from [https://www.python.org/downloads/](https://www.python.org/downloads/).

2. **Pip** (Python package manager)
   Pip should be installed along with Python. If not, install it via [https://pip.pypa.io/en/stable/](https://pip.pypa.io/en/stable/).

3. **Required Libraries**
   Install necessary Python libraries by running:

   ```bash
   pip install -r requirements.txt
   ```

---

### **Cloning the Repository**

To get started, you'll need to clone the **Murph AI** repository to your local machine.

1. **Clone the repository**
   Open a terminal (or Git Bash) and navigate to the directory where you want to store the project. Run the following command to clone the repository:

   ```bash
   git clone https://github.com/amanbangeraa/MurphAi.git
   ```

2. **Navigate into the project folder**
   Once the repo is cloned, navigate into the project directory:

   ```bash
   cd MurphAi
   ```

---

### **Setting Up API Keys (Environment Variables)**

To keep your sensitive information like API keys secure, you should create a `.env` file in the root directory of the project.

1. **Create a `.env` file**
   In your project’s root folder, create a file named `.env`. This file will store your API keys.

2. **Add your API keys to `.env`**
   Open the `.env` file and add the following keys:

   ```ini
   GROQ_API_KEY=your_groq_api_key
   PORCUPINE_ACCESS_KEY=your_porcupine_access_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

   Replace `your_groq_api_key`, `your_porcupine_access_key`, and `your_elevenlabs_api_key` with the actual API keys you have.

---

### **Configuring the `.env` file**

Murph AI uses the `.env` file to securely load API keys and configurations. The application will automatically look for this file when it runs. You do not need to hardcode your keys directly in the code.

---

## **Running Murph AI**

### **1. Run the Python Script**

To start Murph AI, simply run the main script:

```bash
python main.py
```



### **2. Test the Wake Word**

Once you run the script, say the wake word (e.g., "Hey Murph") to activate the assistant.

### **3. Interact with Murph**

Murph will listen to your commands and respond accordingly. You can give it tasks like opening apps, setting reminders, or querying for information.

---

## **Future Features**

* Hand sign detection
* Dedicated hardware for faster processing
* Real-time internet integration for data querying
* Ability to switch between multiple personalities

---

## **Contributing**

If you would like to contribute to the project, feel free to fork the repository and create a pull request with your updates. Contributions, bug fixes, and new features are always welcome!

---

## **License**

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

### **Additional Notes**

* Make sure to **never commit your `.env` file** to GitHub. You can add it to your `.gitignore` to keep it private:

  Add `.env` to the `.gitignore` file:

  ```bash
  .env
  ```

---

This updated README includes instructions for cloning the repo, setting up environment variables, and running Murph AI locally. Let me know if you need further clarification!
