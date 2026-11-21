import sys
import os
import threading
import queue
import time
import math
import datetime
import subprocess

# Auto-configure TCL/TK library path on Windows if needed
base = sys.base_prefix
tcl_dir = os.path.join(base, "tcl", "tcl8.6")
tk_dir = os.path.join(base, "tcl", "tk8.6")
if os.path.isdir(tcl_dir):
    os.environ["TCL_LIBRARY"] = tcl_dir
if os.path.isdir(tk_dir):
    os.environ["TK_LIBRARY"] = tk_dir

import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import main
import tts

# Speech enabled: Assistant speaks aloud ("Opening Google", "Opening YouTube", etc.)
tts.MUTED = False
main.ANNOUNCE_ACTIONS = True

BG_DIR = os.path.join(os.path.dirname(__file__), "Background image")
BG_FITTED = os.path.join(BG_DIR, "Background_fitted.png")
BG_PNG = os.path.join(BG_DIR, "Background.png")
BG_JPG = os.path.join(BG_DIR, "Background.jpg")

def get_or_create_background_image():
    """Ensure a high-quality PNG background is available for Tkinter."""
    if os.path.exists(BG_FITTED):
        return BG_FITTED
    if os.path.exists(BG_PNG):
        return BG_PNG
    if os.path.exists(BG_JPG):
        try:
            cmd = (
                f'Add-Type -AssemblyName System.Drawing; '
                f'$img = [System.Drawing.Image]::FromFile("{BG_JPG}"); '
                f'$img.Save("{BG_PNG}", [System.Drawing.Imaging.ImageFormat]::Png); '
                f'$img.Dispose()'
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
            if os.path.exists(BG_PNG):
                return BG_PNG
        except Exception:
            pass
    return None


class AnimatedMicOrb(tk.Canvas):
    """
    Futuristic glowing animated microphone orb widget.
    Animates pulsing soundwaves and glowing rings based on state:
    - IDLE: Gentle breathing pulse (Cyan/Deep Blue)
    - LISTENING: Rapid energetic wave ripples (Neon Cyan/Green)
    - PROCESSING: Cosmic vortex rotation (Electric Purple)
    - MUTED: Static crimson glow (Coral Red)
    """
    def __init__(self, parent, on_click_callback=None, size=180):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg="#0c1830",
            highlightthickness=0
        )
        self.size = size
        self.center = size / 2
        self.on_click_callback = on_click_callback
        self.state = "idle"
        self.tick = 0
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))
        self._animate()

    def set_state(self, new_state):
        self.state = new_state

    def _handle_click(self, event):
        if self.on_click_callback:
            self.on_click_callback()

    def _animate(self):
        self.delete("all")
        cx, cy = self.center, self.center
        self.tick += 0.08

        # Dynamic state styling
        if self.state == "listening":
            ring_color = "#00f59b"
            core_color = "#00b370"
            glow_color = "#073b27"
            pulse = math.sin(self.tick * 2.5) * 14
        elif self.state == "processing":
            ring_color = "#9d4edd"
            core_color = "#7b2cbf"
            glow_color = "#2a104c"
            pulse = math.sin(self.tick * 2.0) * 10
        elif self.state == "muted":
            ring_color = "#ff4757"
            core_color = "#c0392b"
            glow_color = "#3d1010"
            pulse = 0
        else:  # idle
            ring_color = "#00d2ff"
            core_color = "#0f4c81"
            glow_color = "#0a223f"
            pulse = math.sin(self.tick) * 6

        base_r = self.size * 0.28

        # Outer ripple ring
        if self.state in ("listening", "processing"):
            ripple_r = base_r + 20 + (math.sin(self.tick * 2) * 8)
            self.create_oval(cx - ripple_r, cy - ripple_r, cx + ripple_r, cy + ripple_r,
                              outline=ring_color, width=1)

        # Mid halo ring
        halo_r = base_r + 10 + pulse
        self.create_oval(cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r,
                          fill=glow_color, outline=ring_color, width=2)

        # Core Orb
        self.create_oval(cx - base_r, cy - base_r, cx + base_r, cy + base_r,
                          fill=core_color, outline=ring_color, width=3)

        # Draw Microphone Icon inside core
        self.create_rectangle(cx - 7, cy - 16, cx + 7, cy + 2, fill="#ffffff", outline="")
        self.create_oval(cx - 7, cy - 22, cx + 7, cy - 8, fill="#ffffff", outline="")
        self.create_oval(cx - 7, cy - 4, cx + 7, cy + 10, fill="#ffffff", outline="")

        self.create_arc(cx - 13, cy - 6, cx + 13, cy + 16, start=180, extent=180,
                        style=tk.ARC, outline="#ffffff", width=2)
        self.create_line(cx, cy + 16, cx, cy + 26, fill="#ffffff", width=2)
        self.create_line(cx - 12, cy + 26, cx + 12, cy + 26, fill="#ffffff", width=2)

        self.after(25, self._animate)


class VoiceGlobeGUI:
    """
    Clean interface featuring:
    - Full background image
    - Speak Voice Globe in the center with small speaking/processing glow
    - Right side bottom panel showing all words heard and executed
    - 100% silent execution ("Remove all speaks")
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Voice Assistant - Speak Voice Globe")
        self.root.geometry("780x640")
        self.root.minsize(680, 560)
        self.root.configure(bg="#02030a")

        self.event_queue = queue.Queue()
        self.control_flags = {
            "muted": False,
            "manual_listen": False,
            "running": True
        }

        self.bg_photo = None
        self._load_background_image()
        self._build_ui()
        self._start_listener_thread()
        self._poll_event_queue()

    def _load_background_image(self):
        bg_path = get_or_create_background_image()
        if bg_path and os.path.exists(bg_path):
            try:
                if HAS_PIL:
                    pil_img = Image.open(bg_path).resize((780, 640), Image.Resampling.LANCZOS)
                    self.bg_photo = ImageTk.PhotoImage(pil_img)
                else:
                    self.bg_photo = tk.PhotoImage(file=bg_path)
            except Exception as e:
                print(f"[Notice] Could not load background: {e}")

    def _build_ui(self):
        # 1. Base Canvas with Background Image filling entire window
        self.canvas = tk.Canvas(self.root, width=780, height=640, bg="#02030a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # 2. Centered Speak Voice Globe
        self.orb = AnimatedMicOrb(self.canvas, on_click_callback=self._on_orb_clicked, size=180)
        self.canvas.create_window(310, 270, window=self.orb)

        # 3. Speak Bubble Button
        self.bubble_btn = tk.Button(
            self.canvas,
            text="💬 Speak / Listen",
            font=("Segoe UI", 11, "bold"),
            bg="#132a54",
            fg="#e0edff",
            activebackground="#1d4284",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=22,
            pady=8,
            cursor="hand2",
            command=self._on_orb_clicked
        )
        self.canvas.create_window(310, 400, window=self.bubble_btn)

        # 4. Status pill
        self.status_label = tk.Label(
            self.canvas,
            text="Ready — Click to speak or say 'Hey Windows'",
            font=("Segoe UI", 9),
            fg="#9bb5dc",
            bg="#0b172d",
            padx=14,
            pady=4,
            relief=tk.FLAT
        )
        self.canvas.create_window(310, 450, window=self.status_label)

        # 5. Right Side Bottom Panel: All Words That Take
        transcript_frame = tk.Frame(self.canvas, bg="#081022", bd=1, relief=tk.SOLID, highlightbackground="#244070", highlightthickness=1)
        self.canvas.create_window(630, 490, window=transcript_frame, width=270, height=260)

        # 6. Top Right Side Widget: Live Date & Time
        datetime_frame = tk.Frame(self.canvas, bg="#081022", bd=1, relief=tk.SOLID, highlightbackground="#244070", highlightthickness=1, padx=12, pady=4)
        self.canvas.create_window(630, 52, window=datetime_frame, width=270, height=56)

        self.time_label = tk.Label(datetime_frame, text="--:--:--", font=("Segoe UI", 13, "bold"), fg="#f0f6fc", bg="#081022")
        self.time_label.pack(anchor="e")

        self.date_label = tk.Label(datetime_frame, text="Loading date...", font=("Segoe UI", 8), fg="#8daed8", bg="#081022")
        self.date_label.pack(anchor="e")

        self._update_clock()

        # Header of right-side panel
        header = tk.Frame(transcript_frame, bg="#0e1f3d", pady=4)
        header.pack(fill=tk.X)

        title = tk.Label(header, text="🟢 WORDS HEARD", font=("Segoe UI", 9, "bold"), fg="#b0c8ec", bg="#0e1f3d")
        title.pack(side=tk.LEFT, padx=8)

        clear_btn = tk.Button(
            header, text="Clear", font=("Segoe UI", 8), fg="#6c8db9", bg="#0e1f3d",
            relief=tk.FLAT, bd=0, cursor="hand2", command=self._clear_transcript
        )
        clear_btn.pack(side=tk.RIGHT, padx=6)

        self.words_feed = scrolledtext.ScrolledText(
            transcript_frame, wrap=tk.WORD, bg="#081022", fg="#dce6ff",
            font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=6, state=tk.DISABLED
        )
        self.words_feed.pack(fill=tk.BOTH, expand=True)

        self.words_feed.tag_configure("time", foreground="#5c7ba6", font=("Segoe UI", 8))
        self.words_feed.tag_configure("cmd", foreground="#00f59b", font=("Segoe UI", 9, "bold"))
        self.words_feed.tag_configure("text", foreground="#f0f6fc", font=("Segoe UI", 9))

    def _clear_transcript(self):
        self.words_feed.configure(state=tk.NORMAL)
        self.words_feed.delete("1.0", tk.END)
        self.words_feed.configure(state=tk.DISABLED)

    def _update_clock(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%a, %b %d, %Y")
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        self.root.after(1000, self._update_clock)

    def _add_word_entry(self, text, is_command=False, response_msg=""):
        now_str = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.words_feed.configure(state=tk.NORMAL)
        self.words_feed.insert(tk.END, f"[{now_str}]\n", "time")
        if is_command:
            self.words_feed.insert(tk.END, f"⚡ {text}\n", "cmd")
            if response_msg:
                self.words_feed.insert(tk.END, f"🔊 {response_msg}\n", "cmd")
            self.words_feed.insert(tk.END, "\n")
        else:
            self.words_feed.insert(tk.END, f"\"{text}\"\n\n", "text")
        self.words_feed.see(tk.END)
        self.words_feed.configure(state=tk.DISABLED)

    def _on_orb_clicked(self):
        self.control_flags["manual_listen"] = True

    def _set_state(self, state, text=""):
        self.orb.set_state(state)
        if text:
            self.status_label.config(text=text)
        if state == "listening":
            self.bubble_btn.config(text="🎙️ Listening...", bg="#00f59b", fg="#000000")
            self.status_label.config(fg="#00f59b")
        elif state == "processing":
            self.bubble_btn.config(text="⚡ Executing...", bg="#9d4edd", fg="#ffffff")
            self.status_label.config(fg="#9d4edd")
        else:
            self.bubble_btn.config(text="💬 Speak / Listen", bg="#132a54", fg="#e0edff")
            self.status_label.config(fg="#9bb5dc")

    def _poll_event_queue(self):
        try:
            while True:
                item = self.event_queue.get_nowait()
                ev_type = item[0]
                if ev_type == "status":
                    _, state, text = item
                    self._set_state(state, text)
                elif ev_type == "word":
                    _, word_text, is_cmd, resp_msg = item
                    self._add_word_entry(word_text, is_cmd, resp_msg)
                self.event_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(30, self._poll_event_queue)

    def _start_listener_thread(self):
        threading.Thread(target=self._background_listener_loop, daemon=True).start()

    def _background_listener_loop(self):
        r = sr.Recognizer()
        r.pause_threshold = 0.5
        r.non_speaking_duration = 0.3
        r.phrase_threshold = 0.2

        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.8)
                r.dynamic_energy_threshold = False
                r.energy_threshold = max(r.energy_threshold, 250)
                self.event_queue.put(("status", "idle", "Ready — Click to speak or say 'Hey Windows'"))

                while self.control_flags["running"]:
                    if self.control_flags["muted"]:
                        time.sleep(0.2)
                        continue

                    if self.control_flags.get("manual_listen", False):
                        self.control_flags["manual_listen"] = False
                        self.event_queue.put(("status", "listening", "Listening... speak now"))
                        try:
                            audio = r.listen(source, timeout=6, phrase_time_limit=5)
                            cmd_text = r.recognize_google(audio).strip()
                            self.event_queue.put(("status", "processing", f"Executing: {cmd_text}"))
                            is_ok, spoken_msg = main.processed_command(cmd_text)
                            self.event_queue.put(("word", cmd_text, True, spoken_msg))
                        except Exception:
                            self.event_queue.put(("status", "idle", "Could not understand audio"))
                        finally:
                            time.sleep(1.2)
                            self.event_queue.put(("status", "idle", "Ready — Click to speak or say 'Hey Windows'"))
                        continue

                    # Background Wake Word
                    try:
                        audio = r.listen(source, timeout=None, phrase_time_limit=5)
                        text = r.recognize_google(audio).strip()
                        if text:
                            is_wake, command = main.extract_wake_word_and_command(text, main.WAKE_WORDS)
                            if is_wake and command:
                                self.event_queue.put(("status", "processing", f"Executing: {command}"))
                                is_ok, spoken_msg = main.processed_command(command)
                                self.event_queue.put(("word", command, True, spoken_msg))
                                time.sleep(1.2)
                            elif is_wake:
                                self.event_queue.put(("word", text, False, ""))
                                self.event_queue.put(("status", "listening", "Listening for command..."))
                                cmd_audio = r.listen(source, timeout=5, phrase_time_limit=5)
                                cmd_text = r.recognize_google(cmd_audio).strip()
                                self.event_queue.put(("status", "processing", f"Executing: {cmd_text}"))
                                is_ok, spoken_msg = main.processed_command(cmd_text)
                                self.event_queue.put(("word", cmd_text, True, spoken_msg))
                                time.sleep(1.2)
                            else:
                                self.event_queue.put(("word", text, False, ""))
                    except Exception:
                        pass
                    finally:
                        self.event_queue.put(("status", "idle", "Ready — Click to speak or say 'Hey Windows'"))

        except Exception as e:
            self.event_queue.put(("status", "muted", f"Microphone error: {e}"))


def run_gui():
    root = tk.Tk()
    app = VoiceGlobeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
