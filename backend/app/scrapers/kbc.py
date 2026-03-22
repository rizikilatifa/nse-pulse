"""KBC (Kenya Broadcasting Corporation) scraper."""

import feedparser
import httpx
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.config import settings


class KBCScraper(BaseScraper):
    """Scraper for KBC Kenya (kbc.co.ke)."""

    SOURCE_NAME = "KBC"
    RSS_URL = "https://www.kbc.co.ke/feed/"
    BASE_URL = "https://www.kbc.co.ke"

    async def scrape(self) -> List[dict]:
        """Scrape articles from KBC RSS feed."""
        articles = []

        try:
            async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
                response = await client.get(self.RSS_URL)
                response.raise_for_status()

            feed = feedparser.parse(response.text)

            # KBC feed includes all categories, filter for business-related
            for entry in feed.entries[:settings.max_articles_per_source]:
                # Check if business-related
                categories = [c.get("term", "").lower() for c in entry.get("tags", [])]
                category_str = " ".join(categories)

                article = await self._process_entry(entry, category_str)
                if article:
                    articles.append(article)

        except Exception as e:
            print(f"KBC scraper error: {e}")

        return articles

    async def _process_entry(self, entry, category_str: str = "") -> Optional[dict]:
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

        # Get full content from RSS (prefer content:encoded over summary)
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        if not content:
            content = entry.get("summary", "")

        # Also include categories for matching
        category_str = " ".join([c.get("term", "") for c in entry.get("tags", [])])

        # Match to ticker
        full_text = f"{headline} {content}"
        if category_str:
            full_text += f" {category_str}"
        ticker = self.match_ticker(full_text)

        if not ticker:
            return None

        # Filter: Only include financially relevant articles
        if not self.is_financial_article(full_text):
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Cache-Control": "no-cache",
        }

        async with httpx.AsyncClient(timeout=settings.scrape_timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        selectors = [
            "article",
            ".article-body",
            ".entry-content",
            ".post-content",
            ".content-body",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=" ", strip=True)

        return ""
