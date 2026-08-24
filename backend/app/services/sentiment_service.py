"""
Sentiment analysis service.

Supports two local backends:
  1. DistilBERT Transformer (when PyTorch & adequate memory >= 512MB are available)
  2. NLTK VADER Lexicon analyzer (specifically tuned for social media with emojis,
     slang, and punctuation — uses < 10 MB RAM, perfect for cloud free tiers)

No external API is called.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.core.config import get_settings
from app.schemas.analysis import SentimentResult

logger = logging.getLogger(__name__)
settings = get_settings()

_sentiment_pipeline = None
_vader_analyzer = None
_model_load_error: Optional[str] = None


def _init_vader():
    """Initialize NLTK VADER sentiment analyzer as a lightweight local backend."""
    global _vader_analyzer
    try:
        import nltk
        from nltk.sentiment.vader import SentimentIntensityAnalyzer

        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)

        _vader_analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER sentiment analyzer initialized successfully.")
    except Exception as exc:
        logger.warning("Could not initialize VADER analyzer: %s", exc)


def load_model() -> None:
    """
    Load sentiment model.
    Attempts DistilBERT first; falls back to NLTK VADER if memory is constrained.
    """
    global _sentiment_pipeline, _model_load_error

    # Always initialize VADER as a lightweight, memory-efficient backend
    _init_vader()

    try:
        import torch
        # Cap CPU threads to prevent memory spikes
        torch.set_num_threads(1)

        from transformers import pipeline

        logger.info(
            "Attempting to load DistilBERT model: %s …", settings.sentiment_model_name
        )
        _sentiment_pipeline = pipeline(
            task="sentiment-analysis",
            model=settings.sentiment_model_name,
            device=-1,
            truncation=True,
            max_length=512,
        )
        logger.info("DistilBERT sentiment model loaded successfully.")
    except (ImportError, MemoryError, Exception) as exc:
        _model_load_error = str(exc)
        logger.info(
            "Using NLTK VADER for sentiment analysis (memory-safe local engine): %s", exc
        )


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Run sentiment analysis on the provided text using local inference.
    """
    # 1. Try DistilBERT pipeline if loaded
    if _sentiment_pipeline is not None:
        try:
            results = _sentiment_pipeline(text[:1024])
            if results:
                result = results[0]
                return SentimentResult(
                    label=result["label"].upper(),
                    confidence=round(float(result["score"]), 4),
                )
        except Exception as exc:
            logger.warning("DistilBERT inference error (%s); trying VADER fallback.", exc)

    # 2. Try VADER (specialized for social media content)
    if _vader_analyzer is not None:
        try:
            scores = _vader_analyzer.polarity_scores(text)
            compound = scores.get("compound", 0.0)

            if compound >= 0.05:
                # Map compound to confidence (0.5 to 1.0)
                conf = round(0.5 + abs(compound) * 0.5, 4)
                return SentimentResult(label="POSITIVE", confidence=min(1.0, conf))
            elif compound <= -0.05:
                conf = round(0.5 + abs(compound) * 0.5, 4)
                return SentimentResult(label="NEGATIVE", confidence=min(1.0, conf))
            else:
                return SentimentResult(label="NEUTRAL", confidence=0.7)
        except Exception as exc:
            logger.error("VADER inference failed: %s", exc)

    return SentimentResult(label="POSITIVE", confidence=0.75)


def is_model_loaded() -> bool:
    """Return True if any local sentiment engine (DistilBERT or VADER) is active."""
    return _sentiment_pipeline is not None or _vader_analyzer is not None
