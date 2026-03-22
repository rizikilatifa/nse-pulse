"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings, NSE_COMPANIES
from app.database import init_db, async_session
from app.models import Company
from app.routers import sentiment


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown events."""
    # Startup
    await init_db()
    await seed_companies()
    yield
    # Shutdown (cleanup if needed)
    pass


async def seed_companies():
    """Seed the companies table with NSE top 10."""
    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(Company).limit(1))
        if result.scalar():
            return  # Already seeded

        # Insert companies
        for company_data in NSE_COMPANIES:
            company = Company(**company_data)
            session.add(company)

        await session.commit()
        print(f"Seeded {len(NSE_COMPANIES)} companies")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time sentiment analysis for NSE-listed stocks",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sentiment.router, prefix="/api", tags=["sentiment"])


@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "tickers": "/api/tickers",
            "sentiment": "/api/sentiment/{ticker}",
            "scrape": "/api/scrape",
            "health": "/api/health"
        }
    }


@app.get("/api/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": "connected"
    }


# Serve frontend static files in production
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the frontend SPA for any non-API route."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
