"""Base scraper class with common functionality."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import re


# Financial keywords that indicate investment-relevant content
FINANCIAL_KEYWORDS = [
    # Performance metrics
    "profit", "loss", "revenue", "earnings", "income", "dividend", "yield",
    "growth", "decline", "increase", "decrease", "surge", "drop", "rise",
    # Stock/Market terms
    "stock", "share", "price", "market", "trading", "nse", "ipo", "listing",
    "investor", "investment", "portfolio", "capital", "equity", "valuation",
    # Business operations
    "acquisition", "merger", "buyout", "stake", "ownership", "deal", "contract",
    "expansion", "restructuring", "layoff", "retrenchment", "hire", "ceo", "cfo",
    # Financial reports
    "results", "report", "quarterly", "annual", "financial", "accounts", "audit",
    "balance sheet", "cash flow", "turnover", "margin", "debt", "loan", "credit",
    # Regulatory/Legal
    "regulator", "cbk", "capital markets", "compliance", "fine", "penalty",
    # Economic context
    "interest rate", "inflation", "forex", "currency", "shilling", "dollar",
]

# Non-financial keywords to exclude (sports, entertainment, lifestyle)
EXCLUDE_KEYWORDS = [
    "sports", "football", "rugby", "athletics", "chapa dimba", "tournament",
    "league", "match", "game", "player", "coach", "team", "win", "score",
    "entertainment", "music", "concert", "celebrity", "fashion", "lifestyle",
    "wedding", "relationship", "dating", "recipe", "food", "travel", "tourism",
]


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

    def is_financial_article(self, text: str) -> bool:
        """
        Check if article contains financial/investment-relevant context.

        Args:
            text: Article headline + content

        Returns:
            True if article appears to be financially relevant
        """
        if not text:
            return False

        text_lower = text.lower()

        # First check for exclude keywords
        for keyword in EXCLUDE_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return False

        # Check for financial keywords
        for keyword in FINANCIAL_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True

        return False

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
                keyword_lower = keyword.lower()
                # Use word boundary matching to avoid partial matches
                # e.g., "manageable" should NOT match "eabl"
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text_lower):
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
