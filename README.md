# Ultra-Fast Windows Voice Assistant 🚀

A high-performance, optimized Python voice assistant designed for rapid listening, instant command execution, and non-blocking speech synthesis.

## ⚡ Speed & Latency Optimizations

1. **Instant Silent Action Execution (`ANNOUNCE_ACTIONS = False`)**:
   - Commands like opening websites, opening apps, searching Google/YouTube, or playing music execute **instantly and quietly** without speaking repetitive announcements (*"Opening YouTube"*, *"Searching for..."*, *"Playing music"*).
   - Informational commands (*time*, *date*, *news*, and wake prompts) continue to speak aloud clearly.
   - You can toggle announcements anytime by voice (*"voice mode"* / *"silent mode"*) or by editing `ANNOUNCE_ACTIONS` in `main.py`.
2. **Persistent Microphone Stream**: The microphone is opened and kept active once on startup rather than being opened, closed, and re-opened for every phrase. This saves ~0.5s–1.0s on every command.
3. **Instant Acoustic Tuning**:
   - `pause_threshold = 0.5s` (reduced from 0.8s) – responds 300ms faster when you stop speaking.
   - `non_speaking_duration = 0.3s` – minimizes silence payloads uploaded to Google STT.
   - Fixed ambient calibration at startup eliminates dynamic volume jumping.
4. **Single-Pass Wake-Word Recognition (Listen Fast)**:
   - Say wake-word + command together in one breath: *"Hey Windows open YouTube"* executes **immediately in 1 step**!
   - If only the wake-word is said (*"Hey Windows"*), it gives a short confirmation (*"Yes?"*) and listens for the command.
5. **Native Windows SAPI Speech Engine**:
   - Uses native Windows SAPI with automatic voice token detection, eliminating COM errors and threading freezes.

---

## 🎙️ Supported Commands

### 🌐 Web & Search
- `"Hey Windows, open YouTube"` / `"open google"` / `"open github"` / `"open chatgpt"`
- `"open notion.so"` or any custom domain
- `"search google for quantum physics"`
- `"search youtube for lofi hip hop"`

### 💻 Windows Native Apps
- `"open notepad"`
- `"open calculator"`
- `"open terminal"` / `"open cmd"`
- `"open task manager"`
- `"open explorer"` / `"open files"`
- `"open settings"`
- `"open paint"`

### 🎵 Music & Entertainment
- `"play music"` (plays random playlist or default Spotify playlist)
- `"play naat"` (plays specific track/playlist from `music.txt`)

### 📰 News & Utilities
- `"read news"` / `"latest news"` (fetches top 3 headlines with timeout and clean titles)
- `"what time is it"` / `"time"`
- `"what date is it"` / `"date"`
- `"silent mode"` / `"voice mode"` (toggles action announcements)
- `"stop"` / `"exit"` / `"quit"` / `"goodbye"`

---

## 🛠️ How to Run

1. Activate your virtual environment:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. Start the assistant:
   ```powershell
   python main.py
   ```
