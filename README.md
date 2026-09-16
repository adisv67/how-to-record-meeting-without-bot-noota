# how-to-record-meeting-without-bot-noota by https://www.noota.io/en/how-to-record-meeting-without-bots
cat << 'EOF' > README.md
# PolyMeetAI 🎙️🤖

A **100% local-first, botless meeting assistant** for macOS. Captures system audio directly from your machine, transcribes it in real-time using C++ accelerated AI, and displays live captions in a sleek, scrollable overlay. No cloud, no meeting bots, no privacy concerns.

> **The Problem:** Traditional AI meeting assistants require a "bot" to join your call as a silent participant, which is intrusive and often sends audio to the cloud. 
> **The Solution:** PolyMeetAI intercepts your Mac's local system audio, meaning no bot ever joins the meeting, and 100% of the processing happens on your device.

---

## ✨ Key Features

- **Truly Botless:** No bots join your Google Meet, Zoom, or Teams calls. It operates entirely at the OS audio layer.
- **100% Offline & Private:** Audio is processed in RAM and immediately deleted. Only the text transcript is saved locally to SQLite.
- **Lightning Fast:** Uses `pywhispercpp` (whisper.cpp) with Apple Metal GPU acceleration to generate text in under 2 seconds.
- **Smart Silence Detection:** Uses Silero VAD to only process audio when someone is actually speaking, saving CPU and battery.
- **Modern UI:** A transparent, always-on-top, draggable PySide6 overlay that keeps a scrollable history of the conversation.
- **Local Storage:** Every sentence is automatically logged into a local SQLite database with timestamps.

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Audio Routing | BlackHole 2ch | Virtual audio device to intercept system audio |
| Audio Capture | sounddevice | Read frames from BlackHole into Python |
| Voice Activity | Silero VAD | Detect speech start/end to chunk audio intelligently |
| Speech-to-Text | pywhispercpp | C++ Whisper implementation for Metal-accelerated local transcription |
| Desktop UI | PySide6 (Qt) | Transparent, always-on-top subtitle overlay |
| Storage | SQLite | Local database for transcript persistence |
| Logging | loguru | Structured terminal logging |

---

## ⚙️ System Requirements

- **macOS** on Apple Silicon (M1/M2/M3) - *Optimized for fanless MacBooks*
- **Python 3.12**
- **BlackHole 2ch** (Virtual Audio Driver)

---

## 🚀 Installation & Setup

### 1. System Audio Routing
To capture meeting audio without a bot, you must route your Mac's audio into a virtual device while still being able to hear it.

1. Install [BlackHole 2ch](https://existential.audio/blackhole/).
2. Open macOS **Audio MIDI Setup**.
3. Click the **+** button → **Create Multi-Output Device**.
4. Check the boxes for both **BlackHole 2ch** and your **MacBook Speakers** (or headphones).
5. Set your Mac's System Sound Output to this new **Multi-Output Device**.

### 2. Project Setup
```bash
# Clone or download the project files
cd polymeetai

# Create Python virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt


3. Download the AI Model
The app uses the small Whisper model in C++ .bin format.

mkdir -p models
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin" -o models/ggml-small.bin

💻 Usage
Ensure your Mac's System Sound Output is set to the Multi-Output Device.
Activate the virtual environment and run the app:

source .venv/bin/activate
./run.sh

⚙️ Configuration
You can tune the application by editing polymeetai/config.py:

vad_threshold (0.3): Lower to catch quieter speech. Raise to ignore background noise.
min_silence_duration (0.3): How long (in seconds) the app waits for a pause before transcribing a chunk. Lower = faster, more fragmented subtitles. Higher = slower, cleaner sentences.
whisper_model ("models/ggml-small.bin"): Path to your C++ Whisper model. Can be upgraded to ggml-medium.bin for higher quality.
🛡️ Privacy & Data Flow
PolyMeetAI is local-first by default.

Raw audio exists in memory only long enough for VAD + transcription, then it is discarded (del audio).
Raw audio is never written to disk.
Only the transcribed English text and timestamps are persisted in the local SQLite database.
📁 Project Structure

polymeetai/
├── polymeetai/
│   ├── config.py          # Tunable parameters (VAD, UI, Model paths)
│   ├── audio_capture.py   # sounddevice stream from BlackHole
│   ├── vad.py             # Silero VAD segmentation
│   ├── transcriber.py     # pywhispercpp C++ inference
│   ├── overlay.py         # PySide6 transparent scrollable UI
│   ├── db.py              # SQLite persistence
│   └── main.py            # Thread orchestration & pipeline wiring
├── models/                # Downloaded .bin models
├── requirements.txt
└── run.sh                 # Bash execution script



This README perfectly frames the project as a professional, privacy-first engineering achievement!
