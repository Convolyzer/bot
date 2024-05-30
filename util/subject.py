import aiohttp
import feedparser
from typing import Dict, Optional
from random import choice


class Feed:
    def __init__(self, session, url) -> None:
        self.__url = url
        self.__session = session
        self.__feed = None

    async def __fetch_feed(self):
        """Fetch the raw feed data."""
        async with self.__session.get(self.__url) as resp:
            return await resp.text()

    async def update(self) -> None:
        """Update the feed object."""
        rawdata = await self.__fetch_feed()
        self.__feed = feedparser.parse(rawdata)

    def get_random_entry(self) -> Optional[Dict]:
        """Returns a random entry in the feed."""
        if self.__feed and len(self.__feed["entries"]) > 0:
            return choice(self.__feed["entries"])
        else:
            return None


class Subjector:
    RSS_FEEDS = {
        "Economie": "https://www.france24.com/fr/economie/rss",
        "Opinion": "https://home.cern/fr/api/news/opinion/feed.rss",
        "Politique": "https://services.lesechos.fr/rss/les-echos-politique.xml", 
        "Societe": "https://feeds.leparisien.fr/leparisien/rss/societe",
        "Culture": "https://www.lemonde.fr/culture/rss_full.xml",
        "Sport": "http://dwh.lequipe.fr/api/edito/rss?path=/",
        "Environement": "https://feeds.leparisien.fr/leparisien/rss/societe",
        "Technologie": "https://lejournal.cnrs.fr/rss",
        "Education": "https://edubase.eduscol.education.fr/rss/rss.xml?discipline[0]=Fran%C3%A7ais",
        "Justice": "https://www.lemonde.fr/justice/rss_full.xml",
    }

    def __init__(self) -> None:
        self.__session = aiohttp.ClientSession()
        self.__feeds = {k: Feed(self.__session, v) for k, v in self.RSS_FEEDS.items()}

    async def close(self):
        """Close the http request session."""
        await self.__session.close()

    async def update(self):
        """Update all feed."""
        for feed in self.__feeds.values():
            await feed.update()

    def get_random_entry(self, topic: str) -> Optional[Dict]:
        """Returns a random feed entry on the specified topic."""
        feed = self.__feeds.get(topic)
        if feed:
            return feed.get_random_entry()
        else:
            return None
