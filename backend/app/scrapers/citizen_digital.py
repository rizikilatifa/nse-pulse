"""Citizen Digital scraper."""

import httpx
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup
import json
import re

from app.scrapers.base import BaseScraper
from app.config import settings


class CitizenDigitalScraper(BaseScraper):
    """Scraper for Citizen Digital (citizen.digital)."""

    SOURCE_NAME = "Citizen Digital"
    BASE_URL = "https://citizen.digital"
    BUSINESS_URL = f"{BASE_URL}/business"

    async def scrape(self) -> List[dict]:
        """Scrape articles from Citizen Digital Business section."""
        articles = []

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
                response = await client.get(self.BUSINESS_URL, headers=headers, follow_redirects=True)
                response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Find article links
            article_links = self._extract_article_links(soup)

            # Process unique links
            seen_urls = set()
            for url in article_links[:settings.max_articles_per_source]:
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                try:
                    article = await self._fetch_article(url, headers)
                    if article:
                        articles.append(article)
                except Exception as e:
                    print(f"Citizen Digital article fetch error ({url}): {e}")
                    continue

        except Exception as e:
            print(f"Citizen Digital scraper error: {e}")

        return articles

    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article URLs from the business page."""
        links = []

        # Look for article links
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")

            # Citizen Digital articles typically have numeric IDs in the URL
            # e.g., /business/family-bank-profits-rise-n287731
            if re.search(r'-n\d+$', href) or '/news/' in href or '/business/' in href:
                if href.startswith("/"):
                    href = f"{self.BASE_URL}{href}"
                elif not href.startswith("http"):
                    continue

                # Filter out section pages
                if href.rstrip("/").endswith("/business"):
                    continue

                links.append(href)

        return list(dict.fromkeys(links))

    async def _fetch_article(self, url: str, headers: dict) -> Optional[dict]:
        """Fetch and parse a single article."""
        async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract headline
        headline = None
        for selector in ["h1", ".headline", ".article-title", "[class*='title']"]:
            element = soup.select_one(selector)
            if element:
                headline = element.get_text(strip=True)
                if headline and len(headline) > 10:
                    break

        if not headline:
            title_tag = soup.find("title")
            if title_tag:
                headline = title_tag.get_text(strip=True).split("|")[0].strip()

        if not headline:
            return None

        # Extract content
        content = self._extract_content(soup)

        # Extract date
        published_at = self._extract_date(soup)

        # Match to ticker
        full_text = f"{headline} {content}"
        ticker = self.match_ticker(full_text)

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

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content."""
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "figure"]):
            element.decompose()

        selectors = [
            "article",
            ".article-body",
            ".story-body",
            ".content-body",
            "[class*='article-content']",
            "[class*='story-content']",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=" ", strip=True)

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date."""
        # Try JSON-LD
        script = soup.find("script", type="application/ld+json")
        if script:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                date_str = data.get("datePublished") or data.get("dateCreated")
                if date_str:
                    return self.parse_date(date_str)
            except (json.JSONDecodeError, AttributeError):
                pass

        # Try meta tags
        for meta in soup.find_all("meta"):
            if meta.get("property") in ["article:published_time", "og:published_time"]:
                return self.parse_date(meta.get("content", ""))
            if meta.get("name") in ["publication_date", "date"]:
                return self.parse_date(meta.get("content", ""))

        # Try time elements
        time_elem = soup.find("time")
        if time_elem:
            datetime_attr = time_elem.get("datetime")
            if datetime_attr:
                return self.parse_date(datetime_attr)

        return None
