let mode = "idle"; // "idle", "human", "ai"

// Setup SiriWave
const container = document.getElementById('siri-container');
if (!container) console.error('❌ siri-container not found in HTML!');

const siriWave = new SiriWave({
  container: container,
  width: 1600,
  height: 800,
  style: 'ios',
  speed: 0,
  amplitude: 0,
  autostart: true,
});

// Get transcription elements
const transcriptionContainer = document.getElementById('transcription-container');
const userTranscription = document.getElementById('user-transcription');
const aiTranscription = document.getElementById('ai-transcription');

// Socket.io setup
const socket = io();

socket.on("connect", () => {
  console.log("🔌 Socket connected");
});

socket.on("user-speaking", () => {
  console.log("🎤 User started speaking");
  mode = "human";
});

socket.on("user-speaking-done", () => {
  console.log("🔇 User stopped speaking");
  mode = "idle";
  subtleFadeWave();
});

socket.on("user-transcription", (data) => {
  console.log("📝 User transcription:", data.text);
  userTranscription.textContent = `You: ${data.text}`;
  aiTranscription.textContent = "";
  transcriptionContainer.classList.add('active');
  siriWave.setAmplitude(0.5);
  siriWave.setSpeed(0.1);
});

socket.on("ai-speaking", () => {
  console.log("🤖 AI started speaking");
  mode = "ai";
  siriWave.setAmplitude(0.7);
  siriWave.setSpeed(0.2);
  playAIAudio();
});

socket.on("ai-transcription", (data) => {
  console.log("📝 AI transcription:", data.text);
  aiTranscription.textContent = `AI: ${data.text}`;
  transcriptionContainer.classList.add('active');
  siriWave.setAmplitude(0.6);
  siriWave.setSpeed(0.15);
});

socket.on("ai-speaking-done", () => {
  console.log("🤖 AI stopped speaking");
  mode = "idle";
  subtleFadeWave();
});

// Smooth fade out to a subtle wave
function subtleFadeWave() {
  let amp = siriWave.amplitude;
  const targetAmp = 0.3;
  
  const interval = setInterval(() => {
    if (amp > targetAmp) {
      amp -= 0.05;
      siriWave.setAmplitude(amp);
    } else {
      clearInterval(interval);
      siriWave.setAmplitude(targetAmp);
      siriWave.setSpeed(0.05);
    }
  }, 30);
}

// Original fadeOutWave function
function fadeOutWave() {
  let amp = siriWave.amplitude;
  const interval = setInterval(() => {
    amp -= 0.05;
    if (amp <= 0) {
      amp = 0;
      clearInterval(interval);
    }
    siriWave.setAmplitude(amp);
  }, 30);
}

// AI audio playback and syncing with SiriWave 
function playAIAudio(audioUrl) {
  if (!audioUrl) {
    siriWave.setAmplitude(0.7);
    siriWave.setSpeed(0.2);
    requestAnimationFrame(function animate() {
      if (mode === "ai") {
        siriWave.setAmplitude(0.6 + Math.sin(Date.now() / 1000) * 0.2);
        requestAnimationFrame(animate);
      }
    });
    return;
  }
  
  const audio = new Audio(audioUrl);
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const source = audioContext.createMediaElementSource(audio);
  const analyser = audioContext.createAnalyser();

  source.connect(analyser);
  analyser.connect(audioContext.destination);

  analyser.fftSize = 1024;
  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  audio.play();

  const draw = () => {
    if (mode !== "ai") return;

    analyser.getByteFrequencyData(dataArray);
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
    const avg = sum / dataArray.length;

    const amplitude = (avg / 256) * 1.5 + 0.4;
    siriWave.setAmplitude(amplitude);
    siriWave.setSpeed(0.25);

    requestAnimationFrame(draw);
  };

  draw();

  audio.onended = () => {
    socket.emit("ai-speaking-done");
    mode = "idle";
    subtleFadeWave();
  };
}

// Microphone processing for human voice
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(function(stream) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(stream);
    const scriptProcessor = audioContext.createScriptProcessor(512, 1, 1);

    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 1024;

    microphone.connect(analyser);
    analyser.connect(scriptProcessor);
    scriptProcessor.connect(audioContext.destination);

    scriptProcessor.onaudioprocess = function() {
      if (mode === "human") {
        const array = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(array);

        let values = 0;
        for (let i = 0; i < array.length; i++) {
          values += array[i];
        }

        const average = values / array.length;
        const amplitude = (average / 256) * 1.5 + 0.2;
        siriWave.setAmplitude(amplitude);
        siriWave.setSpeed(0.18);
      }
    };
  })
  .catch(function(err) {
    console.error('Error accessing microphone:', err);
  });
