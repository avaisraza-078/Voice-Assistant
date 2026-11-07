import webbrowser
import random
import time

# Add Spotify playlist link
playlist_url = "https://open.spotify.com/playlist/590kDbLUXhOG5xvidUHMW2?si=71cb178469754389"

def play_music():
    songs = [
        playlist_url
    ]

    random_song = random.choice(songs)

    webbrowser.open(random_song)

    print("Playing random music on Spotify!")

if __name__ == "__main__":
    play_music()