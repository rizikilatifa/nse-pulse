"""SQLAlchemy database models."""

import json
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Company(Base):
    """NSE listed company."""
    __tablename__ = "companies"

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array

    # Relationships
    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="company", cascade="all, delete-orphan"
    )

    def get_keywords(self) -> list[str]:
        """Parse keywords from JSON string."""
        if self.keywords:
            return json.loads(self.keywords)
        return []

    def __repr__(self):
        return f"<Company(ticker={self.ticker}, name={self.name})>"


class Article(Base):
    """Scraped news article."""
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(10), ForeignKey("companies.ticker"), nullable=True)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="articles")
    sentiment: Mapped["SentimentResult"] = relationship(
        "SentimentResult", back_populates="article", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Article(id={self.id}, headline={self.headline[:50]}...)>"


class SentimentResult(Base):
    """Sentiment analysis result for an article."""
    __tablename__ = "sentiment_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("label IN ('positive', 'neutral', 'negative', 'unknown')"),
        nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)  # Confidence 0.0-1.0
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="sentiment")

    def __repr__(self):
        return f"<SentimentResult(article_id={self.article_id}, label={self.label}, score={self.score})>"
