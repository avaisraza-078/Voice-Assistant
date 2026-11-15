# Ultra-Fast Windows Voice Assistant 🚀

A high-performance, silent, and optimized Voice Assistant featuring a **clean, full-screen animated Voice Orb** interface reacting dynamically to your microphone.

---

## 🔮 Voice Orb Frontend (Clean & Minimal)

All screen clutter has been removed, leaving only your **custom background wallpaper**, the **animated 3D glowing speaker globe**, and the **speak bubble button**:

* **Exact Animated Orb Globe**: 6 rotating 3D ribbon loops with dynamic glow, radial halo gradient, and real-time audio reactivity.
* **Full-Screen Background**: Seamlessly displays `Background image/Background.jpg`.
* **Speak Bubble Icon & Button**: Click either the globe or the speak bubble button to speak commands.
* **100% Silent Execution ("Remove all speaks")**: All voice announcements are muted. Commands (*"open youtube"*, *"open google"*, *"play music"*, *"open calculator"*, *"what time is it"*, etc.) execute **instantly and silently**.

---

## 🛠️ How to Run

1. Activate your virtual environment:
   ```powershell
   .\.venv\Scripts\activate
   ```

2. Run the assistant (launches the clean Voice Orb UI in your browser):
   ```powershell
   python main.py
   ```
   *(or run `python server.py` directly, which opens `http://127.0.0.1:5000`)*

3. Or run the clean Desktop Window GUI:
   ```powershell
   python main.py --gui
   ```

4. Or run in headless Terminal mode:
   ```powershell
   python main.py --cli
   ```
