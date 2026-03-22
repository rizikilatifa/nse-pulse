"""Sentiment API router."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Company, Article, SentimentResult
from app.schemas import (
    TickerListResponse,
    CompanyResponse,
    TickerSentimentResponse,
    SentimentDetail,
    HeadlineWithSentiment,
    ScrapeResponse,
    ErrorResponse
)
from app.scrapers import run_all_scrapers
from app.sentiment.analyzer import analyze_sentiment

router = APIRouter()


@router.get("/tickers", response_model=TickerListResponse)
async def get_tickers(
    session: AsyncSession = Depends(get_session)
):
    """
    Get all tracked tickers with aggregated sentiment.
    Returns list of 10 NSE companies with their current sentiment status.
    """
    # Get all companies
    result = await session.execute(select(Company).order_by(Company.ticker))
    companies = result.scalars().all()

    tickers = []
    last_scraped = None

    for company in companies:
        # Get article count and aggregated sentiment for this ticker
        article_result = await session.execute(
            select(
                func.count(Article.id).label("count"),
                func.avg(SentimentResult.score).label("avg_score")
            )
            .select_from(Article)
            .outerjoin(SentimentResult, Article.id == SentimentResult.article_id)
            .where(Article.ticker == company.ticker)
        )
        article_data = article_result.first()

        # Get most common sentiment label
        label_result = await session.execute(
            select(
                SentimentResult.label,
                func.count(SentimentResult.id).label("count")
            )
            .join(Article, Article.id == SentimentResult.article_id)
            .where(Article.ticker == company.ticker)
            .group_by(SentimentResult.label)
            .order_by(desc("count"))
            .limit(1)
        )
        label_data = label_result.first()

        article_count = article_data.count if article_data else 0
        avg_score = float(article_data.avg_score) if article_data and article_data.avg_score else None
        sentiment_label = label_data.label if label_data else None

        tickers.append(CompanyResponse(
            ticker=company.ticker,
            name=company.name,
            sector=company.sector,
            sentiment_label=sentiment_label,
            sentiment_score=avg_score,
            article_count=article_count
        ))

    # Get last scraped time
    last_scraped_result = await session.execute(
        select(func.max(Article.scraped_at))
    )
    last_scraped = last_scraped_result.scalar()

    return TickerListResponse(
        tickers=tickers,
        total=len(tickers),
        last_scraped=last_scraped
    )


@router.get("/sentiment/{ticker}", response_model=TickerSentimentResponse)
async def get_ticker_sentiment(
    ticker: str,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=3, ge=1, le=10, description="Number of headlines to return")
):
    """
    Get detailed sentiment for a specific ticker.
    Returns aggregated sentiment and top headlines.
    """
    ticker = ticker.upper()

    # Get company
    company_result = await session.execute(
        select(Company).where(Company.ticker == ticker)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' not found. Valid tickers: SCOM, EQTY, KCB, EABL, NCBA, COOP, ABSA, SCBK, BRIT, BAT"
        )

    # Get aggregated sentiment
    sentiment_result = await session.execute(
        select(
            func.count(Article.id).label("count"),
            func.avg(SentimentResult.score).label("avg_score")
        )
        .select_from(Article)
        .outerjoin(SentimentResult, Article.id == SentimentResult.article_id)
        .where(Article.ticker == ticker)
    )
    sentiment_data = sentiment_result.first()

    # Get most common label
    label_result = await session.execute(
        select(
            SentimentResult.label,
            func.count(SentimentResult.id).label("count")
        )
        .join(Article, Article.id == SentimentResult.article_id)
        .where(Article.ticker == ticker)
        .group_by(SentimentResult.label)
        .order_by(desc("count"))
        .limit(1)
    )
    label_data = label_result.first()

    article_count = sentiment_data.count if sentiment_data else 0
    avg_score = float(sentiment_data.avg_score) if sentiment_data and sentiment_data.avg_score else None
    sentiment_label = label_data.label if label_data else None

    # Handle no articles case
    if article_count == 0:
        return TickerSentimentResponse(
            ticker=company.ticker,
            company_name=company.name,
            sector=company.sector,
            sentiment=SentimentDetail(
                label=None,
                score=None,
                article_count=0
            ),
            top_headlines=[],
            last_updated=None
        )

    # Get top headlines with sentiment
    headlines_result = await session.execute(
        select(Article, SentimentResult)
        .outerjoin(SentimentResult, Article.id == SentimentResult.article_id)
        .where(Article.ticker == ticker)
        .order_by(desc(Article.published_at))
        .limit(limit)
    )
    headlines_data = headlines_result.all()

    top_headlines = []
    for article, sentiment in headlines_data:
        top_headlines.append(HeadlineWithSentiment(
            headline=article.headline,
            url=article.url,
            source=article.source,
            sentiment=sentiment.label if sentiment else None,
            score=float(sentiment.score) if sentiment else None,
            published_at=article.published_at
        ))

    # Get last updated time
    last_updated_result = await session.execute(
        select(func.max(Article.scraped_at)).where(Article.ticker == ticker)
    )
    last_updated = last_updated_result.scalar()

    return TickerSentimentResponse(
        ticker=company.ticker,
        company_name=company.name,
        sector=company.sector,
        sentiment=SentimentDetail(
            label=sentiment_label,
            score=avg_score,
            article_count=article_count
        ),
        top_headlines=top_headlines,
        last_updated=last_updated
    )


@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    session: AsyncSession = Depends(get_session)
):
    """
    Trigger manual scrape of all news sources.
    Fetches articles, analyzes sentiment, and stores results.
    """
    try:
        articles = await run_all_scrapers(session)

        # Analyze sentiment for each article
        processed = 0
        errors = []

        for article in articles:
            try:
                # Get text to analyze (headline + content)
                text = article.headline
                if article.content:
                    text = f"{article.headline}. {article.content[:500]}"

                # Analyze sentiment
                sentiment_data = analyze_sentiment(text)

                # Store sentiment result
                sentiment = SentimentResult(
                    article_id=article.id,
                    label=sentiment_data["label"],
                    score=sentiment_data["score"]
                )
                session.add(sentiment)
                processed += 1

            except Exception as e:
                errors.append(f"Failed to process article {article.id}: {str(e)}")

        await session.commit()

        return ScrapeResponse(
            status="success",
            articles_scraped=len(articles),
            articles_processed=processed,
            errors=errors
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )
