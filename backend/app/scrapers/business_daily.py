"""Business Daily Africa scraper."""

import feedparser
import httpx
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.config import settings, NEWS_SOURCES


class BusinessDailyScraper(BaseScraper):
    """Scraper for Business Daily Africa."""

    SOURCE_NAME = "Business Daily"
    RSS_URL = NEWS_SOURCES["business_daily"]["rss_url"]
    BASE_URL = NEWS_SOURCES["business_daily"]["base_url"]

    async def scrape(self) -> list[dict]:
        """Scrape articles from Business Daily RSS feed."""
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
            print(f"Business Daily scraper error: {e}")

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

        # Try to fetch full article content
        content = entry.get("summary", "")
        try:
            content = await self._fetch_article_content(url)
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
        async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Try common article content selectors
        selectors = [
            "article",
            ".article-content",
            ".story-content",
            "[data-testid='article-content']",
            ".post-content",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=" ", strip=True)

        return ""
