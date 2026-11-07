import speech_recognition as sr
import pyttsx3
import webbrowser
from music_player import play_music
from news import get_news

# recognizer = sr.Recognizer()

# speak function to convert text to speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def processed_command(command):
    command = command.lower()

    websites = {
        "open google": "https://www.google.com",
        "open youtube": "https://www.youtube.com",
        "open facebook": "https://www.facebook.com",
        "open twitter": "https://www.x.com",
        "open instagram": "https://www.instagram.com",
        "open github": "https://www.github.com",
        "open stackoverflow": "https://stackoverflow.com",
        "open linkedin": "https://www.linkedin.com",
        "open reddit": "https://www.reddit.com",
        "open pinterest": "https://www.pinterest.com",
        "open whatsapp": "https://web.whatsapp.com",
        "open telegram": "https://web.telegram.org",
        "open gmail": "https://mail.google.com",
        "open drive": "https://drive.google.com",
        "open maps": "https://maps.google.com",
        "open amazon": "https://www.amazon.in",
        "open flipkart": "https://www.flipkart.com",
        "open netflix": "https://www.netflix.com",
        "open spotify": "https://www.spotify.com",
        "open chatgpt": "https://chatgpt.com",
        "open microsoft": "https://www.microsoft.com",
        "open wikipedia": "https://www.wikipedia.org",
        "open canva": "https://www.canva.com",
        "open discord": "https://discord.com",
        "open twitch": "https://www.twitch.tv",
        "open zoom": "https://zoom.us",
        "open coursera": "https://www.coursera.org",
        "open geeksforgeeks": "https://www.geeksforgeeks.org",
        "open w3schools": "https://www.w3schools.com",
        "open codepen": "https://codepen.io"
    }

    #Website commands
    for key, url in websites.items():
        if key in command:
            speak("Opening " + key.replace("open ", ""))
            webbrowser.open(url)
            return

    # Music commands
    if "play random music" in command or "play music" in command:
        speak("Playing music")
        play_music()
        return

    # News commands
    if "read news" in command or "latest news" in command:
        get_news(speak)
        return

    speak("Sorry, command not recognized")


if __name__ == "__main__":

    # define wake word
    wake_words = [
        "windows",
        "hello windows",
        "hey windows",
        "ok windows"
    ]

    speak("Initalizing Windows Voice Assistant")

    while True:

            # obtain audio from the microphone
        r = sr.Recognizer()

        # recognize speech using google
        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening for the activation word...")
                audio = r.listen(source, timeout=5, phrase_time_limit=3)

            word = r.recognize_google(audio)
            print("You said:", word)

            # check if the recognized word contains any of the wake words
            if any(wake_word in word.lower() for wake_word in wake_words):
                speak("Windows activated")

                # listen for commands
                with sr.Microphone() as source:
                    print("Windows Activated...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)

                    processed_command(command)

        except sr.WaitTimeoutError:
            print("Listening timed out")
        
        except sr.UnknownValueError:
            print("Could not understand audio")

        except sr.RequestError as e:
            print("Speech recognition error:", e)
        
        except Exception as e:
            print("Error:", e)