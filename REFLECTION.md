# Written Reflection: NSE Pulse Implementation

## Trade-offs Made

### 1. Sentiment Model: FinBERT + VADER Fallback

**Decision**: Used a hybrid approach instead of fine-tuning a custom model.

**Rationale**: No publicly available labeled sentiment dataset exists for Kenyan/NSE financial news. FinBERT, trained on financial text from SEC filings and earnings calls, provides reasonable out-of-the-box performance for financial sentiment. VADER serves as a lightweight fallback if the model fails to load.

**Trade-off**: May miss Kenya-specific context (e.g., "harambee" or local business terminology) that a fine-tuned model would capture.

### 2. Scraping: RSS Feeds Instead of Full HTML Parsing

**Decision**: Prioritized RSS feeds with content extraction as a secondary step.

**Rationale**: RSS is cleaner, less brittle, and sites explicitly support it. Full HTML parsing breaks when site structures change—a common maintenance headache.

**Trade-off**: Some articles may lack full content if the extraction fails, limiting sentiment accuracy.

### 3. SQLite vs PostgreSQL

**Decision**: Used SQLite with async SQLAlchemy.

**Rationale**: Zero configuration for an assessment; easy to upgrade to PostgreSQL later. The async pattern future-proofs the code for production scaling.

**Trade-off**: Single-file database won't scale for concurrent writes in heavy production use.

### 4. Manual Scrape Trigger

**Decision**: Scraping is triggered manually via API instead of a background scheduler.

**Rationale**: Simpler for demo purposes; demonstrates the full pipeline without infrastructure complexity.

**Trade-off**: In production, you'd want scheduled scraping (e.g., every 4 hours) with APScheduler or Celery.

## What I'd Do Differently With More Time

1. **Fine-tune on NSE Headlines**: Collect ~500 manually labeled NSE headlines and fine-tune FinBERT for better local context.

2. **Add More News Sources**: Include The Standard, Citizen Business, and NSE's own announcements feed.

3. **Implement Caching**: Add Redis for caching sentiment results to reduce database load.

4. **Add Historical Tracking**: Store daily sentiment snapshots to show trends over time.

5. **Improve Error Handling**: Add retry logic with exponential backoff for failed scrapes.

6. **Add Authentication**: Simple API key authentication for production deployment.

7. **Rate Limiting**: Protect the `/api/scrape` endpoint from abuse.

## What I'd Do With Real NSE Data Access

With direct access to NSE data feeds:

1. **Real-time Price Correlation**: Correlate sentiment with actual price movements to validate the signal.

2. **Corporate Actions Integration**: Factor in dividends, stock splits, and announcements that affect sentiment.

3. **Volume-Weighted Sentiment**: Weight article sentiment by market volume during publication.

4. **Insider Trading Detection**: Cross-reference sentiment spikes with insider trading patterns.

5. **Sector-Level Aggregation**: Group sentiment by sector (Banking, Manufacturing) for macro insights.

---

*This reflection is part of the AfCEN Hazina platform assessment.*
