import http.server
import socketserver
import webbrowser
import urllib.parse
import os
import json
import threading
import sys
import speech_recognition as sr

import main
import tts

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "Background image", "Background.jpg")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

# Ensure all speech is muted ("Remove all speaks")
tts.MUTED = True
main.ANNOUNCE_ACTIONS = False

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

        # 3. API Command Endpoint (Silent execution)
        if parsed.path == "/api/command":
            params = urllib.parse.parse_qs(parsed.query)
            cmd = params.get("cmd", [""])[0]
            print(f"\n[Web Command Received]: '{cmd}'")

            if cmd:
                # Execute command silently without speaking
                try:
                    main.processed_command(cmd)
                    res = {"status": "ok", "command": cmd}
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

        # Fallback to default
        super().do_GET()

    def log_message(self, format, *args):
        # Keep terminal output clean
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

                    is_wake, command = main.extract_wake_word_and_command(text, main.WAKE_WORDS)
                    if is_wake and command:
                        print(f"[Mic Heard]: '{command}'")
                        main.processed_command(command)
                except Exception:
                    pass
    except Exception as e:
        print(f"[Notice] Background mic listener disabled: {e}")


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), VoiceOrbRequestHandler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print("=" * 60)
        print(f"      WINDOWS VOICE ASSISTANT - ORB FRONTEND")
        print("=" * 60)
        print(f"[*] Serving Voice Orb at: {url}")
        print("[*] Silent execution active ('Remove all speaks')")
        print("[*] Opening browser...")

        # Open in default web browser
        webbrowser.open(url)

        # Start background listener in parallel thread
        threading.Thread(target=background_mic_listener, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server Stopped]")


if __name__ == "__main__":
    run_server()
