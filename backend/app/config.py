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
    scrape_timeout: int = 60
    max_articles_per_source: int = 50

    # Twitter API (optional)
    twitter_bearer_token: str = ""

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
        "base_url": "https://www.businessdailyafrica.com",
        "type": "rss"
    },
    "nation": {
        "name": "Nation Business",
        "rss_url": "https://nation.africa/kenya/business/rss",
        "base_url": "https://nation.africa",
        "type": "rss",
        "status": "blocked"  # 403 Forbidden
    },
    "the_star": {
        "name": "The Star Kenya",
        "base_url": "https://www.the-star.co.ke",
        "business_url": "https://www.the-star.co.ke/business",
        "type": "web"
    },
    "citizen_digital": {
        "name": "Citizen Digital",
        "base_url": "https://citizen.digital",
        "business_url": "https://citizen.digital/business",
        "type": "web"
    },
    "capital_fm": {
        "name": "Capital FM Kenya",
        "rss_url": "https://capitalfm.co.ke/business/feed/",
        "base_url": "https://capitalfm.co.ke",
        "type": "rss"
    },
    "kenya_wall_street": {
        "name": "Kenya Wall Street",
        "rss_url": "https://www.kenyawallstreet.com/feed/",
        "base_url": "https://www.kenyawallstreet.com",
        "type": "rss"
    },
    "kbc": {
        "name": "KBC Kenya",
        "rss_url": "https://www.kbc.co.ke/feed/",
        "base_url": "https://www.kbc.co.ke",
        "type": "rss"
    },
    "pulse_live": {
        "name": "Pulse Live Kenya",
        "rss_url": "https://www.pulse.co.ke/business/rss",
        "base_url": "https://www.pulse.co.ke",
        "type": "rss"
    },
    "twitter": {
        "name": "Twitter/X",
        "type": "api",
        "requires_auth": True,
        "env_key": "TWITTER_BEARER_TOKEN",
        "note": "Requires Basic tier ($100/mo) for search access"
    }
}
