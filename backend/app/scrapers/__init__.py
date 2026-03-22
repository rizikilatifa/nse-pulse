"""Scrapers package."""

from app.scrapers.base import BaseScraper
from app.scrapers.business_daily import BusinessDailyScraper
from app.scrapers.nation import NationScraper
from app.config import NSE_COMPANIES
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Article, Company
from sqlalchemy import select
import json
import asyncio


SCRAPERS = [
    BusinessDailyScraper,
    NationScraper,
]


async def run_all_scrapers(session: AsyncSession) -> list[Article]:
    """Run all scrapers and return collected articles."""
    all_articles = []

    # Get company keywords for matching
    companies_data = {}
    result = await session.execute(select(Company))
    companies = result.scalars().all()

    for company in companies:
        keywords = company.get_keywords()
        companies_data[company.ticker] = {
            "name": company.name,
            "keywords": keywords
        }

    # Run each scraper
    for ScraperClass in SCRAPERS:
        try:
            scraper = ScraperClass(companies_data)
            articles = await scraper.scrape()
            all_articles.extend(articles)
        except Exception as e:
            print(f"Scraper {ScraperClass.__name__} failed: {e}")
            continue

    # Store articles in database
    stored_articles = []
    for article_data in all_articles:
        # Check if article already exists
        existing = await session.execute(
            select(Article).where(Article.url == article_data["url"])
        )
        if existing.scalar_one_or_none():
            continue

        article = Article(
            ticker=article_data.get("ticker"),
            headline=article_data["headline"],
            url=article_data["url"],
            source=article_data["source"],
            content=article_data.get("content"),
            published_at=article_data.get("published_at")
        )
        session.add(article)
        stored_articles.append(article)

    await session.commit()

    # Refresh to get IDs
    for article in stored_articles:
        await session.refresh(article)

    return stored_articles
