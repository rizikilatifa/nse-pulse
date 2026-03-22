"""Twitter/X scraper using API v2.

Note: This scraper requires Twitter API credentials.
To use:
1. Sign up at https://developer.twitter.com
2. Create a project and app
3. Get Bearer Token from your app settings
4. Set TWITTER_BEARER_TOKEN environment variable
"""

import httpx
from datetime import datetime
from typing import Optional, List
import os

from app.scrapers.base import BaseScraper
from app.config import settings


class TwitterScraper(BaseScraper):
    """Scraper for Twitter/X using API v2."""

    SOURCE_NAME = "Twitter/X"
    API_BASE = "https://api.twitter.com/2"

    # Search queries for NSE companies
    SEARCH_QUERIES = [
        "Safaricom OR M-Pesa",
        "Equity Bank OR Equity Group",
        "KCB Bank OR KCB Group",
        "EABL OR East African Breweries",
        "NCBA Bank OR NCBA Group",
        "Co-op Bank OR Cooperative Bank Kenya",
        "Absa Kenya OR Barclays Kenya",
        "Standard Chartered Kenya OR Stanchart",
        "Britam OR British American Insurance Kenya",
        "BAT Kenya",
        "NSE Kenya OR Nairobi Securities Exchange",
    ]

    def __init__(self, companies_data: dict):
        super().__init__(companies_data)
        self.bearer_token = settings.twitter_bearer_token or os.getenv("TWITTER_BEARER_TOKEN")

    async def scrape(self) -> List[dict]:
        """Scrape tweets about NSE companies."""
        if not self.bearer_token:
            print("Twitter scraper: No TWITTER_BEARER_TOKEN found. Skipping.")
            return []

        articles = []

        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=settings.scrape_timeout) as client:
                for query in self.SEARCH_QUERIES[:5]:  # Limit queries per scrape
                    try:
                        tweets = await self._search_tweets(client, query, headers)
                        articles.extend(tweets)
                    except Exception as e:
                        print(f"Twitter query error ({query}): {e}")
                        continue

        except Exception as e:
            print(f"Twitter scraper error: {e}")

        return articles

    async def _search_tweets(self, client: httpx.AsyncClient, query: str, headers: dict) -> List[dict]:
        """Search for tweets matching a query."""
        url = f"{self.API_BASE}/tweets/search/recent"
        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": 20,
            "tweet.fields": "created_at,text,public_metrics",
            "expansions": "author_id",
            "user.fields": "name,username",
        }

        response = await client.get(url, headers=headers, params=params)

        if response.status_code == 401:
            print("Twitter API: Invalid or expired token")
            return []

        if response.status_code == 429:
            print("Twitter API: Rate limit exceeded")
            return []

        response.raise_for_status()
        data = response.json()

        articles = []
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}

        for tweet in data.get("data", []):
            article = self._process_tweet(tweet, users)
            if article:
                articles.append(article)

        return articles

    def _process_tweet(self, tweet: dict, users: dict) -> Optional[dict]:
        """Process a tweet into article format."""
        text = tweet.get("text", "")
        tweet_id = tweet.get("id")
        author_id = tweet.get("author_id")
        created_at = tweet.get("created_at")

        if not text or not tweet_id:
            return None

        # Match to ticker
        ticker = self.match_ticker(text)
        if not ticker:
            return None

        # Get author info
        author = users.get(author_id, {})
        author_name = author.get("name", "Unknown")
        author_username = author.get("username", "unknown")

        # Build URL
        url = f"https://twitter.com/{author_username}/status/{tweet_id}"

        # Parse date
        published_at = None
        if created_at:
            published_at = self.parse_date(created_at)

        # Use tweet text as headline (truncate if needed)
        headline = text[:200] + "..." if len(text) > 200 else text

        return {
            "headline": self.clean_text(headline),
            "url": url,
            "source": f"{self.SOURCE_NAME} (@{author_username})",
            "content": self.clean_text(text),
            "published_at": published_at,
            "ticker": ticker
        }
