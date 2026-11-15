import sys

class NativeTTS:
    """
    High-performance native Windows SAPI Text-to-Speech engine.
    Initializes in ~5ms without COM voice token bugs or pyttsx3 threading freezes.
    """
    def __init__(self, rate: int = 1, volume: int = 100):
        self._speaker = None
        self.rate = rate
        self.volume = volume
        self._init_engine()

    def _init_engine(self):
        try:
            import win32com.client
            self._speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Explicitly assign voice token to bypass missing DefaultTokenId registry issue on Windows 11
            try:
                cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices", False)
                tokens = cat.EnumerateTokens()
                if tokens.Count > 0:
                    self._speaker.Voice = tokens.Item(0)
            except Exception:
                pass

            self._speaker.Rate = self.rate
            self._speaker.Volume = self.volume
        except Exception:
            # Fallback to pyttsx3 if win32com is not available
            try:
                import pyttsx3
                self._speaker = pyttsx3.init()
                self._speaker.setProperty("rate", 190)
            except Exception as ex:
                self._speaker = None
                print(f"[TTS Warning] TTS engine could not be initialized: {ex}")

    def speak(self, text: str, block: bool = True):
        """
        Speak text clearly using native SAPI.
        block=True waits until speech completes before continuing,
        preventing the microphone from recording the assistant's own voice.
        """
        if not text:
            return
        print(f"\n[Assistant]: {text}")
        if self._speaker is None:
            return

        try:
            if hasattr(self._speaker, "Speak"):
                flags = 0 if block else 1  # SVSFDefault = 0, SVSFlagsAsync = 1
                self._speaker.Speak(text, flags)
            elif hasattr(self._speaker, "say"):
                self._speaker.say(text)
                self._speaker.runAndWait()
        except Exception:
            # Prevent crashes if audio output is temporarily unavailable
            pass


# Global mute flag: Set to True to remove all speech output ("Remove all speaks")
MUTED = True

_tts_instance = None

def get_tts(rate: int = 1) -> NativeTTS:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = NativeTTS(rate=rate)
    return _tts_instance

def speak(text: str, block: bool = True):
    """Speaks text using native SAPI, or stays completely silent when MUTED=True."""
    if MUTED or not text:
        if text:
            print(f"[Assistant (Silent)]: {text}")
        return
    get_tts().speak(text, block=block)
