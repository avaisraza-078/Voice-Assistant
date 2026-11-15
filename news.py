import feedparser
import random
import re
import urllib.request

NEWS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

def clean_headline(title: str) -> str:
    """Strip publisher suffixes like ' - The Indian Express' for faster, cleaner TTS."""
    clean = re.sub(r"\s*-\s*[^-]+$", "", title)
    return clean.strip() or title

def get_news(speak_func, count: int = 3):
    """
    Fetch and read top news headlines quickly.
    Defaults to 3 headlines for speed and low listening fatigue.
    """
    speak_func("Fetching latest news...", block=False)

    try:
        # Fetch RSS with a 5-second timeout to avoid long hangs
        req = urllib.request.Request(
            NEWS_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()

        feed = feedparser.parse(xml_data)
        articles = feed.entries

        if not articles:
            speak_func("No news headlines found right now.", block=True)
            return

        selected = articles[:count]

        print("\n" + "=" * 30)
        print("      LATEST HEADLINES       ")
        print("=" * 30)

        for index, article in enumerate(selected, start=1):
            title = clean_headline(article.title)
            print(f"{index}. {title}")
            speak_func(f"Headline {index}: {title}", block=True)

        speak_func("That is all for the latest news.", block=False)

    except Exception as e:
        print(f"[News Error]: {e}")
        speak_func("Sorry, could not retrieve news headlines.", block=False)

if __name__ == "__main__":
    from tts import speak
    get_news(speak)
