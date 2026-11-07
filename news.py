import feedparser
import random

def get_news(speak):
    speak("Getting the latest news")

    news_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(news_url)

    if not feed.entries:
        speak("Sorry, unable to get the news")
        return

    # Get all available headlines
    articles = feed.entries

    # Select 5 random headlines
    random_news = random.sample(
        articles,
        min(5, len(articles))
    )

    print("\n===== RANDOM LATEST NEWS =====\n")

    for index, article in enumerate(random_news, start=1):
        title = article.title

        print(f"{index}. {title}")

        speak(title)

    speak("That is all for today's news")