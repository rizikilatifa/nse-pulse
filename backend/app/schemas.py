"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Company Schemas ============

class CompanyBase(BaseModel):
    """Base company schema."""
    ticker: str
    name: str
    sector: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Company response with sentiment data."""
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    article_count: int = 0

    class Config:
        from_attributes = True


# ============ Article Schemas ============

class ArticleBase(BaseModel):
    """Base article schema."""
    headline: str
    url: str
    source: Optional[str] = None
    published_at: Optional[datetime] = None


class ArticleResponse(ArticleBase):
    """Article response with sentiment."""
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

    class Config:
        from_attributes = True


# ============ Sentiment Schemas ============

class SentimentDetail(BaseModel):
    """Detailed sentiment for a ticker."""
    label: Optional[str] = None
    score: Optional[float] = Field(None, ge=0.0, le=1.0)
    article_count: int = 0


class HeadlineWithSentiment(BaseModel):
    """Headline with sentiment data."""
    headline: str
    url: str
    source: Optional[str] = None
    sentiment: Optional[str] = None
    score: Optional[float] = None
    published_at: Optional[datetime] = None


class TickerSentimentResponse(BaseModel):
    """Full sentiment response for a ticker."""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    sentiment: SentimentDetail
    top_headlines: List[HeadlineWithSentiment] = []
    last_updated: Optional[datetime] = None


# ============ API Response Schemas ============

class TickerListResponse(BaseModel):
    """Response for ticker list endpoint."""
    tickers: List[CompanyResponse]
    total: int
    last_scraped: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    app_name: str
    version: str
    database: str = "connected"


class ScrapeResponse(BaseModel):
    """Response for scrape trigger endpoint."""
    status: str
    articles_scraped: int
    articles_processed: int
    errors: List[str] = []


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
