import speech_recognition as sr
import webbrowser
import datetime
import urllib.parse
import os
import sys
import re

from tts import speak, get_tts
from music_player import play_music
from news import get_news

# Set to True so the assistant always speaks aloud ("Opening Google", "Opening YouTube", etc.)
ANNOUNCE_ACTIONS = True

# Pre-indexed websites for instant O(1) lookup
WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
    "instagram": "https://www.instagram.com",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "pinterest": "https://www.pinterest.com",
    "whatsapp": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "maps": "https://maps.google.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://www.spotify.com",
    "chatgpt": "https://chatgpt.com",
    "microsoft": "https://www.microsoft.com",
    "wikipedia": "https://www.wikipedia.org",
    "canva": "https://www.canva.com",
    "discord": "https://discord.com",
    "twitch": "https://www.twitch.tv",
    "zoom": "https://zoom.us",
    "coursera": "https://www.coursera.org",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "w3schools": "https://www.w3schools.com",
    "codepen": "https://codepen.io"
}

# Native Windows applications for fast local launch
APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "terminal": "wt",
    "cmd": "cmd",
    "command prompt": "cmd",
    "explorer": "explorer",
    "file explorer": "explorer",
    "task manager": "taskmgr",
    "settings": "start ms-settings:",
    "paint": "mspaint"
}

WAKE_WORDS = [
    "windows",
    "hello windows",
    "hey windows",
    "ok windows"
]

def extract_wake_word_and_command(text: str, wake_words: list[str]) -> tuple[bool, str]:
    """
    Checks if text contains any wake word.
    Returns (is_wake_word_detected, remaining_command).
    
    If the user says wake word and command together (e.g. 'Hey Windows open YouTube'),
    it extracts the command directly for 1-step instant execution.
    """
    text = text.lower().strip()
    sorted_wakes = sorted(wake_words, key=len, reverse=True)

    for wake in sorted_wakes:
        if text.startswith(wake):
            remainder = text[len(wake):].strip().lstrip(",.!? ")
            return True, remainder

        pattern = r"\b" + re.escape(wake) + r"\b"
        match = re.search(pattern, text)
        if match:
            remainder = text[match.end():].strip().lstrip(",.!? ")
            return True, remainder

    return False, ""

def processed_command(command: str) -> tuple[bool, str]:
    """
    Executes recognized commands and speaks confirmations aloud.
    Returns (keep_running, spoken_message).
    """
    global ANNOUNCE_ACTIONS
    cmd = command.lower().strip()
    if not cmd:
        return True, ""

    print(f"[Executing Command]: '{cmd}'")

    # 1. Exit / Stop Commands
    if cmd in ("exit", "quit", "stop", "goodbye", "bye", "sleep", "shut down"):
        msg = "Goodbye!"
        speak(msg, block=True)
        return False, msg

    # 2. Toggle Action Announcements
    if cmd in ("silent mode", "mute announcements", "disable announcements", "quiet mode"):
        ANNOUNCE_ACTIONS = False
        msg = "Action announcements disabled."
        speak(msg, block=True)
        return True, msg

    if cmd in ("voice mode", "enable announcements", "unmute announcements"):
        ANNOUNCE_ACTIONS = True
        msg = "Action announcements enabled."
        speak(msg, block=True)
        return True, msg

    # 3. Time & Date Commands (Always spoken aloud)
    if any(q in cmd for q in ("what time is it", "current time", "tell me the time")) or cmd == "time":
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        msg = f"The time is {now_str}"
        speak(msg, block=True)
        return True, msg

    if any(q in cmd for q in ("what date is it", "today's date", "what is the date")) or cmd == "date":
        date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
        msg = f"Today is {date_str}"
        speak(msg, block=True)
        return True, msg

    # 4. Direct YouTube Search
    if cmd.startswith("search youtube for ") or cmd.startswith("youtube "):
        query = cmd.replace("search youtube for ", "").replace("youtube ", "").strip()
        if query:
            msg = f"Searching YouTube for {query}"
            speak(msg, block=True)
            webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}")
            return True, msg

    # 5. Direct Google Search
    if cmd.startswith("search google for ") or cmd.startswith("search for ") or cmd.startswith("google "):
        query = cmd.replace("search google for ", "").replace("search for ", "").replace("google ", "").strip()
        if query:
            msg = f"Searching Google for {query}"
            speak(msg, block=True)
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
            return True, msg

    # 6. Open Apps or Websites
    if cmd.startswith("open "):
        target = cmd[5:].strip()

        # Check local Windows Apps first
        if target in APPS:
            msg = f"Opening {target}"
            speak(msg, block=True)
            os.system(f"start {APPS[target]}")
            return True, msg

        # Check pre-indexed websites (O(1) hash lookup)
        if target in WEBSITES:
            msg = f"Opening {target.title()}"
            speak(msg, block=True)
            webbrowser.open(WEBSITES[target])
            return True, msg

        # Check if user specified a domain (e.g. 'open github.com' or 'open example.org')
        if "." in target and " " not in target:
            url = target if target.startswith("http") else f"https://{target}"
            msg = f"Opening {target}"
            speak(msg, block=True)
            webbrowser.open(url)
            return True, msg

        # Fallback to direct .com URL
        fallback_url = f"https://www.{target}.com"
        msg = f"Opening {target}"
        speak(msg, block=True)
        webbrowser.open(fallback_url)
        return True, msg

    # 7. Music Commands
    if "play" in cmd and ("music" in cmd or "song" in cmd or "spotify" in cmd or "naat" in cmd):
        song_query = cmd.replace("play", "").replace("random", "").replace("music", "").replace("song", "").strip()
        track_name = play_music(song_query)
        msg = f"Playing {track_name}"
        speak(msg, block=True)
        return True, msg

    # 8. News Commands (Always spoken)
    if any(k in cmd for k in ("read news", "latest news", "news", "headlines")):
        get_news(speak, count=3)
        return True, "Reading latest news"

    # 9. Unhandled queries: Fall back to Google Search
    print(f"[Fallback]: Searching web for '{cmd}'")
    msg = f"Searching for {cmd}"
    speak(msg, block=True)
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(cmd)}")
    return True, msg


def run_assistant():
    """Main loop with persistent microphone and fast audio processing."""
    r = sr.Recognizer()

    # Fast audio tuning: lower pause threshold for rapid utterance completion
    r.pause_threshold = 0.5            # Respond 300ms faster after speech stops (default 0.8s)
    r.non_speaking_duration = 0.3      # Minimize silence buffer (default 0.5s)
    r.phrase_threshold = 0.2           # Fast phrase detection (default 0.3s)

    # Initialize native TTS early
    get_tts(rate=1)

    print("=" * 55)
    print("      WINDOWS VOICE ASSISTANT (HIGH SPEED)      ")
    print("=" * 55)

    try:
        # Keep microphone stream open to eliminate device re-initialization lag
        with sr.Microphone() as source:
            print("\n[Calibrating ambient noise... please stay quiet for a moment]")
            r.adjust_for_ambient_noise(source, duration=0.8)
            r.dynamic_energy_threshold = False  # Lock threshold to prevent floating delays
            r.energy_threshold = max(r.energy_threshold, 250)

            speak("Windows Voice Assistant ready.", block=True)
            print("[Ready! Wake words: 'Windows', 'Hey Windows', 'OK Windows']")

            while True:
                print("\n[Listening...]")
                try:
                    # phrase_time_limit prevents long hangs on background noise
                    audio = r.listen(source, timeout=None, phrase_time_limit=5)
                    text = r.recognize_google(audio).strip()
                    print(f"[Heard]: \"{text}\"")

                    is_wake, command = extract_wake_word_and_command(text, WAKE_WORDS)

                    if is_wake:
                        # 1-step execution: Wake word + command said together
                        if command:
                            keep_running, _ = processed_command(command)
                            if not keep_running:
                                break
                        else:
                            # 2-step execution: Wake word only said, prompt for command
                            speak("Yes?", block=True)
                            print("[Listening for command...]")
                            try:
                                cmd_audio = r.listen(source, timeout=5, phrase_time_limit=5)
                                cmd_text = r.recognize_google(cmd_audio).strip()
                                keep_running, _ = processed_command(cmd_text)
                                if not keep_running:
                                    break
                            except sr.WaitTimeoutError:
                                print("[Listening timed out]")
                            except sr.UnknownValueError:
                                print("[Could not understand command]")

                except sr.UnknownValueError:
                    # Silence or unrecognized audio
                    pass
                except sr.RequestError as e:
                    print(f"[Network/API Error]: {e}")
                    speak("Speech recognition network error", block=True)
                except Exception as e:
                    print(f"[Error]: {e}")

    except KeyboardInterrupt:
        print("\n[Voice Assistant Stopped by User]")
    except Exception as e:
        print(f"\n[Fatal Error opening microphone]: {e}")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_assistant()
    elif "--gui" in sys.argv:
        try:
            from gui import run_gui
            run_gui()
        except Exception as e:
            run_assistant()
    else:
        try:
            from server import run_server
            run_server()
        except Exception as e:
            try:
                from gui import run_gui
                run_gui()
            except Exception:
                run_assistant()
