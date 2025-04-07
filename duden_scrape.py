# duden_scrape.py
import feedparser
from datetime import datetime

def get_wort_des_tages():
    feed = feedparser.parse("https://www.duden.de/wort-des-tages/feed")
    today = datetime.utcnow().date()

    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6]).date()
        if published == today:
            return f"{entry.title}: {entry.link}"
    return None
