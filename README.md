# NSE Pulse

Real-time sentiment analysis engine for Nairobi Securities Exchange (NSE) listed stocks.

## Overview

NSE Pulse is a mini sentiment feed for the top 10 NSE-listed stocks. It scrapes Kenyan financial news, analyzes sentiment using NLP, and displays results in a React dashboard.

### Features

- **Data Ingestion**: Scrapes articles from Business Daily Africa and Nation Business
- **Sentiment Analysis**: Hybrid approach using FinBERT (financial-domain BERT) with VADER fallback
- **REST API**: FastAPI backend with endpoints for tickers and sentiment data
- **Dashboard**: React frontend with real-time sentiment visualization

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, SQLAlchemy, aiosqlite |
| Scraping | feedparser, httpx, BeautifulSoup |
| NLP | FinBERT (ProsusAI/finbert), VADER |
| Database | SQLite |
| Frontend | React, Vite, Tailwind CSS |
| Deployment | Railway (backend), Vercel (frontend) |

## Project Structure

```
nse-pulse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings and constants
│   │   ├── database.py          # SQLite connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── scrapers/            # News scrapers
│   │   ├── sentiment/           # Sentiment analysis
│   │   └── routers/             # API endpoints
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── api/
│   └── package.json
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Git

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickers` | List all tracked tickers with sentiment |
| GET | `/api/sentiment/{ticker}` | Get sentiment details for a ticker |
| POST | `/api/scrape` | Trigger news scraping |
| GET | `/api/health` | Health check |

### Example Response: GET /api/sentiment/SCOM

```json
{
  "ticker": "SCOM",
  "company_name": "Safaricom PLC",
  "sector": "Telecommunications",
  "sentiment": {
    "label": "positive",
    "score": 0.78,
    "article_count": 12
  },
  "top_headlines": [
    {
      "headline": "Safaricom reports record M-Pesa transactions",
      "url": "https://...",
      "source": "Business Daily",
      "sentiment": "positive",
      "score": 0.85,
      "published_at": "2024-01-15T10:30:00"
    }
  ],
  "last_updated": "2024-01-15T14:22:00"
}
```

## Tracked Stocks

| Ticker | Company | Sector |
|--------|---------|--------|
| SCOM | Safaricom PLC | Telecommunications |
| EQTY | Equity Group Holdings | Banking |
| KCB | KCB Group Ltd | Banking |
| EABL | East African Breweries Ltd | Manufacturing |
| NCBA | NCBA Group PLC | Banking |
| COOP | Co-operative Bank of Kenya | Banking |
| ABSA | Absa Bank Kenya PLC | Banking |
| SCBK | Standard Chartered Bank Kenya | Banking |
| BRIT | Britam Holdings Ltd | Insurance |
| BAT | British American Tobacco Kenya | Manufacturing |

## Deployment

### Backend (Railway)

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Add environment variables from `.env.example`
5. Deploy

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Set the root directory to `frontend`
4. Add environment variable: `VITE_API_URL` = your Railway backend URL
5. Deploy

## Trade-offs and Design Decisions

### Sentiment Model Choice

**Chosen**: Hybrid approach - FinBERT with VADER fallback

**Rationale**:
- FinBERT is trained on financial text and outperforms generic sentiment models
- VADER provides a fast, rule-based fallback if FinBERT fails to load
- No labeled NSE-specific dataset exists, so pre-trained models are the practical choice

**With more time**: Would collect labeled NSE headlines for fine-tuning

### Scraping Strategy

**Chosen**: RSS feeds + HTTP content extraction

**Rationale**:
- RSS is cleaner and sites expect it to be consumed
- More reliable than full HTML parsing
- `feedparser` handles RSS variations well

**With more time**: Would add The Standard, add rate limiting, implement caching

### Database

**Chosen**: SQLite with SQLAlchemy async

**Rationale**:
- Zero configuration for the assessment scope
- Async support via aiosqlite
- Easy to upgrade to PostgreSQL for production

### Frontend

**Chosen**: React + Vite + Tailwind CSS

**Rationale**:
- Fast development with Vite's HMR
- Tailwind for rapid styling
- Simple state management (no Redux needed for this scope)

## Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| No articles for ticker | Returns `article_count: 0`, `sentiment: null` |
| Scraping fails | Logs error, continues with other sources |
| Unknown ticker | Returns 404 with helpful error message |
| Duplicate articles | URL unique constraint prevents duplicates |
| Sentiment model fails | Falls back to VADER, then returns "neutral" |

## Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## License

MIT

## Author

Built for AfCEN's Hazina platform assessment.
