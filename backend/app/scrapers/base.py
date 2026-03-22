"""Base scraper class with common functionality."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import re


class BaseScraper(ABC):
    """Abstract base class for news scrapers."""

    def __init__(self, companies_data: dict):
        """
        Initialize scraper with company data for keyword matching.

        Args:
            companies_data: Dict mapping ticker to company info and keywords
                           e.g., {"SCOM": {"name": "Safaricom", "keywords": ["Safaricom", "M-Pesa"]}}
        """
        self.companies_data = companies_data

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """
        Scrape articles from the source.

        Returns:
            List of article dicts with keys:
            - headline: str
            - url: str
            - source: str
            - content: Optional[str]
            - published_at: Optional[datetime]
            - ticker: Optional[str] (matched company)
        """
        pass

    def match_ticker(self, text: str) -> Optional[str]:
        """
        Match article text to a company ticker using keywords.

        Args:
            text: Article headline or content to match

        Returns:
            Matched ticker or None
        """
        if not text:
            return None

        text_lower = text.lower()

        for ticker, data in self.companies_data.items():
            for keyword in data["keywords"]:
                if keyword.lower() in text_lower:
                    return ticker

        return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        if not date_str:
            return None

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%a, %d %b %Y %H:%M:%S %z",  # RSS format
            "%a, %d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None
