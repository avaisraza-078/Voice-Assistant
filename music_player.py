import webbrowser
import random
import os
import re

DEFAULT_PLAYLIST = "https://open.spotify.com/playlist/590kDbLUXhOG5xvidUHMW2?si=71cb178469754389"
MUSIC_FILE = os.path.join(os.path.dirname(__file__), "music.txt")

def load_music_library():
    """Load songs/playlists from music.txt into a normalized dictionary."""
    library = {}
    if os.path.exists(MUSIC_FILE):
        try:
            with open(MUSIC_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        name, url = line.split("=", 1)
                        library[name.strip().lower()] = url.strip()
        except Exception as e:
            print(f"[Music] Error loading music.txt: {e}")
    return library

def play_music(song_query: str = ""):
    """
    Play music immediately on Spotify or browser.
    If song_query matches an entry in music.txt, plays that specific link.
    Otherwise plays a random selection or the default playlist.
    """
    library = load_music_library()
    target_url = None
    target_name = None

    if song_query:
        query_clean = song_query.lower().strip()
        # Direct key match
        for name, url in library.items():
            if name in query_clean or query_clean in name:
                target_url = url
                target_name = name.title()
                break

    # If no specific match, choose random from library or default playlist
    if not target_url:
        if library:
            target_name, target_url = random.choice(list(library.items()))
            target_name = target_name.title()
        else:
            target_url = DEFAULT_PLAYLIST
            target_name = "Spotify Playlist"

    print(f"[Music] Playing {target_name}: {target_url}")
    webbrowser.open(target_url)
    return target_name

if __name__ == "__main__":
    play_music()
