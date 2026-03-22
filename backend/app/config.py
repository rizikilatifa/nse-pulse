"""Application configuration and constants."""

from pydantic_settings import BaseSettings
from typing import List, Dict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "NSE Pulse"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./nse_pulse.db"

    # Sentiment Model
    use_finbert: bool = True
    finbert_model: str = "ProsusAI/finbert"
    model_cache_dir: str = "./model_cache"

    # Scraping
    scrape_timeout: int = 30
    max_articles_per_source: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# NSE Top 10 Companies
NSE_COMPANIES: List[Dict[str, str]] = [
    {
        "ticker": "SCOM",
        "name": "Safaricom PLC",
        "sector": "Telecommunications",
        "keywords": '["Safaricom", "M-Pesa", "Safaricom PLC"]'
    },
    {
        "ticker": "EQTY",
        "name": "Equity Group Holdings",
        "sector": "Banking",
        "keywords": '["Equity Bank", "Equity Group", "Equity Holdings"]'
    },
    {
        "ticker": "KCB",
        "name": "KCB Group Ltd",
        "sector": "Banking",
        "keywords": '["KCB Bank", "KCB Group", "Kenya Commercial Bank"]'
    },
    {
        "ticker": "EABL",
        "name": "East African Breweries Ltd",
        "sector": "Manufacturing",
        "keywords": '["EABL", "East African Breweries", "Tusker", "Guinness Kenya"]'
    },
    {
        "ticker": "NCBA",
        "name": "NCBA Group PLC",
        "sector": "Banking",
        "keywords": '["NCBA", "NCBA Group", "NIC Bank", "CBA Bank"]'
    },
    {
        "ticker": "COOP",
        "name": "Co-operative Bank of Kenya",
        "sector": "Banking",
        "keywords": '["Co-op Bank", "Cooperative Bank", "Co-operative Bank"]'
    },
    {
        "ticker": "ABSA",
        "name": "Absa Bank Kenya PLC",
        "sector": "Banking",
        "keywords": '["Absa Kenya", "Absa Bank", "Barclays Kenya"]'
    },
    {
        "ticker": "SCBK",
        "name": "Standard Chartered Bank Kenya",
        "sector": "Banking",
        "keywords": '["Stanchart", "Standard Chartered Kenya", "Standard Chartered Bank Kenya"]'
    },
    {
        "ticker": "BRIT",
        "name": "Britam Holdings Ltd",
        "sector": "Insurance",
        "keywords": '["Britam", "British American Insurance", "Britam Holdings"]'
    },
    {
        "ticker": "BAT",
        "name": "British American Tobacco Kenya",
        "sector": "Manufacturing",
        "keywords": '["BAT Kenya", "British American Tobacco Kenya"]'
    },
]

# News Sources
NEWS_SOURCES = {
    "business_daily": {
        "name": "Business Daily Africa",
        "rss_url": "https://www.businessdailyafrica.com/bd/rss.xml",
        "base_url": "https://www.businessdailyafrica.com"
    },
    "nation": {
        "name": "Nation Business",
        "rss_url": "https://nation.africa/kenya/business/rss",
        "base_url": "https://nation.africa"
    }
}
