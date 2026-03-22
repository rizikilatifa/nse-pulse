"""Nation Business scraper."""

import feedparser
import httpx
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.config import settings, NEWS_SOURCES


class NationScraper(BaseScraper):
    """Scraper for Nation Business (nation.africa)."""

    SOURCE_NAME = "Nation Business"
    RSS_URL = NEWS_SOURCES["nation"]["rss_url"]
    BASE_URL = NEWS_SOURCES["nation"]["base_url"]

    async def scrape(self) -> list[dict]:
        """Scrape articles from Nation Business RSS feed."""
        articles = []

        try:
            # Fetch RSS feed
            async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
                response = await client.get(self.RSS_URL)
                response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries[:settings.max_articles_per_source]:
                article = await self._process_entry(entry)
                if article:
                    articles.append(article)

        except Exception as e:
            print(f"Nation scraper error: {e}")

        return articles

    async def _process_entry(self, entry) -> Optional[dict]:
        """Process a single RSS entry."""
        headline = entry.get("title", "")
        url = entry.get("link", "")

        if not headline or not url:
            return None

        # Parse publication date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        elif entry.get("published"):
            published_at = self.parse_date(entry.published)

        # Get summary/content from RSS
        content = entry.get("summary", "")

        # Try to fetch full article content
        try:
            full_content = await self._fetch_article_content(url)
            if full_content:
                content = full_content
        except Exception:
            pass  # Use summary as fallback

        # Match to ticker
        full_text = f"{headline} {content}"
        ticker = self.match_ticker(full_text)

        # Only include articles that match our tickers
        if not ticker:
            return None

        return {
            "headline": self.clean_text(headline),
            "url": url,
            "source": self.SOURCE_NAME,
            "content": self.clean_text(content)[:2000] if content else None,
            "published_at": published_at,
            "ticker": ticker
        }

    async def _fetch_article_content(self, url: str) -> str:
        """Fetch full article content from URL."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Try common article content selectors for Nation
        selectors = [
            "article",
            ".article-body",
            ".story-body",
            "[data-testid='article-body']",
            ".content-body",
            ".article-content",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=" ", strip=True)

        return ""
