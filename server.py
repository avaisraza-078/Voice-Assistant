import http.server
import socketserver
import webbrowser
import urllib.parse
import os
import json
import threading
import sys
import datetime
import speech_recognition as sr

import main
import tts

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "Background image", "Background.jpg")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

# Assistant speaks words aloud ("Opening Google", "Opening YouTube", etc.)
tts.MUTED = False
main.ANNOUNCE_ACTIONS = True

# Shared in-memory list of words/commands for the bottom-right panel
RECOGNIZED_WORDS = []
WORDS_LOCK = threading.Lock()

def add_word_event(text: str, is_command: bool = True, response: str = ""):
    now_str = datetime.datetime.now().strftime("%I:%M:%S %p")
    with WORDS_LOCK:
        RECOGNIZED_WORDS.append({
            "time": now_str,
            "text": text,
            "is_command": is_command,
            "response": response
        })
        # Keep latest 50 entries
        if len(RECOGNIZED_WORDS) > 50:
            RECOGNIZED_WORDS.pop(0)

class VoiceOrbRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. Serve index.html
        if parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if os.path.exists(INDEX_PATH):
                with open(INDEX_PATH, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"<h1>index.html not found</h1>")
            return

        # 2. Serve background image
        if parsed.path in ("/background.jpg", "/background"):
            if os.path.exists(BG_PATH):
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                with open(BG_PATH, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 3. API Command Endpoint (Executes & speaks aloud)
        if parsed.path == "/api/command":
            params = urllib.parse.parse_qs(parsed.query)
            cmd = params.get("cmd", [""])[0]
            print(f"\n[Command Received]: '{cmd}'")

            if cmd:
                try:
                    is_ok, spoken_msg = main.processed_command(cmd)
                    add_word_event(cmd, is_command=True, response=spoken_msg)
                    res = {"status": "ok", "command": cmd, "speech": spoken_msg}
                except Exception as e:
                    res = {"status": "error", "message": str(e)}
            else:
                res = {"status": "empty"}

            response_bytes = json.dumps(res).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_bytes)
            return

        # 4. API Words Endpoint (Syncs words to right-side bottom widget)
        if parsed.path == "/api/words":
            with WORDS_LOCK:
                data = list(RECOGNIZED_WORDS)
            response_bytes = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_bytes)
            return

        super().do_GET()

    def log_message(self, format, *args):
        pass


def background_mic_listener():
    """Background Python listener so wake words work even outside the browser."""
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    r.non_speaking_duration = 0.3
    r.phrase_threshold = 0.2

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            r.dynamic_energy_threshold = False
            r.energy_threshold = max(r.energy_threshold, 250)

            while True:
                try:
                    audio = r.listen(source, timeout=None, phrase_time_limit=5)
                    text = r.recognize_google(audio).strip()
                    if text:
                        print(f"[Mic Heard]: \"{text}\"")
                        is_wake, command = main.extract_wake_word_and_command(text, main.WAKE_WORDS)
                        if is_wake and command:
                            is_ok, spoken_msg = main.processed_command(command)
                            add_word_event(command, is_command=True, response=spoken_msg)
                        else:
                            add_word_event(text, is_command=False)
                except Exception:
                    pass
    except Exception as e:
        print(f"[Notice] Background mic listener disabled: {e}")


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), VoiceOrbRequestHandler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print("=" * 60)
        print("      WINDOWS VOICE ASSISTANT - SPEAK VOICE GLOBE")
        print("=" * 60)
        print(f"[*] Serving Speak Voice Globe at: {url}")
        print("[*] Silent execution active ('Remove all speaks')")
        print("[*] Opening browser...")

        webbrowser.open(url)
        threading.Thread(target=background_mic_listener, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server Stopped]")


if __name__ == "__main__":
    run_server()
