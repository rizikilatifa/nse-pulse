"""Archive scraper to fetch historical articles from news sites."""

import httpx
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup
import re
import asyncio

from app.scrapers.base import BaseScraper
from app.config import settings


class ArchiveScraper(BaseScraper):
    """Scraper for historical articles from news archive pages."""

    # Archive URLs with pagination support
    ARCHIVE_SOURCES = [
        {
            "name": "Business Daily - Companies",
            "url": "https://www.businessdailyafrica.com/bd/corporate/companies",
            "selector": ".article-list article a, .story-list a, .article-item a",
        },
        {
            "name": "Business Daily - Markets",
            "url": "https://www.businessdailyafrica.com/bd/markets",
            "selector": ".article-list article a, .story-list a, .article-item a",
        },
        {
            "name": "Citizen Digital - Business",
            "url": "https://citizen.digital/business/",
            "selector": "a[href*='/article/'], .article-card a, .news-item a",
        },
        {
            "name": "Kenya Wall Street",
            "url": "https://www.kenyawallstreet.com/category/business/",
            "selector": "article a, .post a, .entry-title a",
        },
    ]

    async def scrape(self) -> List[dict]:
        """Scrape historical articles from archive pages."""
        all_articles = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }

        for source in self.ARCHIVE_SOURCES:
            try:
                articles = await self._scrape_archive(source, headers)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Archive scraper error ({source['name']}): {e}")

        return all_articles

    async def _scrape_archive(self, source: dict, headers: dict) -> List[dict]:
        """Scrape articles from a single archive source."""
        articles = []

        async with httpx.AsyncClient(timeout=settings.scrape_timeout, follow_redirects=True) as client:
            # Scrape multiple pages (page 1, 2, 3)
            for page in range(1, 4):
                try:
                    url = source["url"]
                    if page > 1:
                        # Try common pagination patterns
                        if "?" in url:
                            url = f"{url}&page={page}"
                        else:
                            url = f"{url.rstrip('/')}/page/{page}/"

                    response = await client.get(url, headers=headers)
                    if response.status_code != 200:
                        break

                    soup = BeautifulSoup(response.text, "html.parser")
                    links = soup.select(source["selector"])

                    seen_urls = set()
                    for link in links[:20]:  # Limit per page
                        href = link.get("href", "")
                        if not href:
                            continue

                        if href.startswith("/"):
                            href = f"https://{httpx.URL(source['url']).host}{href}"

                        if href in seen_urls:
                            continue
                        seen_urls.add(href)

                        # Fetch and process article
                        article = await self._fetch_article(href, headers, source["name"])
                        if article:
                            articles.append(article)

                except Exception as e:
                    print(f"Page {page} error for {source['name']}: {e}")
                    break

        return articles

    async def _fetch_article(self, url: str, headers: dict, source_name: str) -> Optional[dict]:
        """Fetch and process a single article."""
        try:
            async with httpx.AsyncClient(timeout=settings.scrape_timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract headline
            headline = None
            for selector in ["h1", ".headline", ".article-title", ".entry-title", "[class*='title']"]:
                element = soup.select_one(selector)
                if element:
                    headline = element.get_text(strip=True)
                    if headline and len(headline) > 15:
                        break

            if not headline:
                return None

            # Extract content
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            content = ""
            for selector in ["article", ".article-body", ".entry-content", ".post-content", ".content-body", "[class*='content']"]:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator=" ", strip=True)[:3000]
                    break

            # Extract date
            published_at = self._extract_date(soup)

            # Match to ticker
            full_text = f"{headline} {content}"
            ticker = self.match_ticker(full_text)

            if not ticker:
                return None

            # Filter: Only financially relevant
            if not self.is_financial_article(full_text):
                return None

            return {
                "headline": self.clean_text(headline),
                "url": url,
                "source": source_name,
                "content": self.clean_text(content)[:2000] if content else None,
                "published_at": published_at,
                "ticker": ticker
            }

        except Exception as e:
            return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date from article page."""
        import json

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
            except:
                pass

        # Try meta tags
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "")
            if prop in ["article:published_time", "og:published_time", "datePublished"]:
                return self.parse_date(meta.get("content", ""))
            name = meta.get("name", "")
            if name in ["publication_date", "date", "dc.date"]:
                return self.parse_date(meta.get("content", ""))

        # Try time element
        time_elem = soup.find("time")
        if time_elem:
            datetime_attr = time_elem.get("datetime")
            if datetime_attr:
                return self.parse_date(datetime_attr)

        return None
