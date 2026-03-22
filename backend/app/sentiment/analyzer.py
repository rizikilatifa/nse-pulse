"""Sentiment analyzer with FinBERT and VADER fallback."""

import os
from typing import Literal
from app.config import settings

# Global model instances
_finbert_pipeline = None
_vader_analyzer = None


def _get_finbert():
    """Lazy load FinBERT model."""
    global _finbert_pipeline

    if _finbert_pipeline is not None:
        return _finbert_pipeline

    if not settings.use_finbert:
        return None

    try:
        from transformers import pipeline
        import torch

        # Set cache directory
        os.makedirs(settings.model_cache_dir, exist_ok=True)

        # Load FinBERT pipeline
        _finbert_pipeline = pipeline(
            "sentiment-analysis",
            model=settings.finbert_model,
            device=-1,  # Use CPU
            cache_dir=settings.model_cache_dir
        )
        print("FinBERT model loaded successfully")
        return _finbert_pipeline

    except Exception as e:
        print(f"Failed to load FinBERT: {e}")
        return None


def _get_vader():
    """Lazy load VADER analyzer."""
    global _vader_analyzer

    if _vader_analyzer is not None:
        return _vader_analyzer

    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _vader_analyzer = SentimentIntensityAnalyzer()
        print("VADER analyzer loaded successfully")
        return _vader_analyzer

    except Exception as e:
        print(f"Failed to load VADER: {e}")
        return None


def _finbert_to_label(label: str) -> str:
    """Convert FinBERT labels to standard format."""
    label_map = {
        "positive": "positive",
        "negative": "negative",
        "neutral": "neutral"
    }
    return label_map.get(label.lower(), "neutral")


def _vader_to_label(compound: float) -> str:
    """Convert VADER compound score to label."""
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    return "neutral"


def _vader_score_to_confidence(compound: float) -> float:
    """Convert VADER compound score to confidence (0-1)."""
    # Compound is -1 to 1, convert to 0 to 1 confidence
    return abs(compound)


def analyze_sentiment(
    text: str
) -> dict[Literal["label"], str] | dict[Literal["score"], float]:
    """
    Analyze sentiment of text using FinBERT with VADER fallback.

    Args:
        text: Text to analyze

    Returns:
        Dict with 'label' (positive/neutral/negative) and 'score' (0.0-1.0)
    """
    if not text or not text.strip():
        return {"label": "neutral", "score": 0.5}

    text = text[:512]  # Truncate for model limits

    # Try FinBERT first
    finbert = _get_finbert()
    if finbert:
        try:
            result = finbert(text)[0]
            label = _finbert_to_label(result["label"])
            score = result["score"]
            return {"label": label, "score": float(score)}
        except Exception as e:
            print(f"FinBERT analysis failed: {e}")

    # Fallback to VADER
    vader = _get_vader()
    if vader:
        try:
            scores = vader.polarity_scores(text)
            label = _vader_to_label(scores["compound"])
            confidence = _vader_score_to_confidence(scores["compound"])
            return {"label": label, "score": confidence}
        except Exception as e:
            print(f"VADER analysis failed: {e}")

    # Final fallback - return neutral
    return {"label": "neutral", "score": 0.5}


def get_aggregate_sentiment(sentiments: list[dict]) -> dict:
    """
    Aggregate multiple sentiment results.

    Args:
        sentiments: List of sentiment dicts with 'label' and 'score'

    Returns:
        Aggregated sentiment with most common label and average score
    """
    if not sentiments:
        return {"label": None, "score": None, "count": 0}

    # Count labels
    label_counts = {}
    for s in sentiments:
        label = s["label"]
        label_counts[label] = label_counts.get(label, 0) + 1

    # Get most common label
    most_common_label = max(label_counts, key=label_counts.get)

    # Calculate average score
    scores = [s["score"] for s in sentiments if s["score"] is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    return {
        "label": most_common_label,
        "score": avg_score,
        "count": len(sentiments)
    }
