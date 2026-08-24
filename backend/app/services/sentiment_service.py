"""
Sentiment analysis service using a pretrained DistilBERT Transformer.

The model is loaded ONCE at application startup via the `load_model()` function
called from the FastAPI lifespan handler. Subsequent requests reuse the cached
pipeline, avoiding per-request model loading overhead.

Model: distilbert-base-uncased-finetuned-sst-2-english
Source: Hugging Face Hub (downloaded on first use, cached locally)
"""

from __future__ import annotations

import logging
from typing import Optional

from app.core.config import get_settings
from app.schemas.analysis import SentimentResult

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level pipeline reference — populated by load_model()
_sentiment_pipeline = None
_model_load_error: Optional[str] = None


def load_model() -> None:
    """
    Load the DistilBERT sentiment pipeline.
    Called once during application startup. Errors are captured and surfaced
    gracefully — the rest of the app still works without sentiment.
    """
    global _sentiment_pipeline, _model_load_error

    try:
        from transformers import pipeline

        logger.info(
            "Loading sentiment model: %s …", settings.sentiment_model_name
        )
        _sentiment_pipeline = pipeline(
            task="sentiment-analysis",
            model=settings.sentiment_model_name,
            # Limit memory: use float32 on CPU (no GPU assumed in dev)
            device=-1,
            truncation=True,
            max_length=512,
        )
        logger.info("Sentiment model loaded successfully.")
    except Exception as exc:
        _model_load_error = str(exc)
        logger.error("Failed to load sentiment model: %s", exc)


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Run sentiment analysis on the provided text.

    The text is truncated to 512 tokens automatically by the pipeline.
    If the model failed to load, returns a neutral fallback with low confidence.

    Args:
        text: Preprocessed post text.

    Returns:
        SentimentResult with label and confidence.
    """
    if _sentiment_pipeline is None:
        logger.warning("Sentiment model not available; returning neutral fallback.")
        return SentimentResult(
            label="NEUTRAL",
            confidence=0.5,
        )

    try:
        results = _sentiment_pipeline(text[:1024])  # Hard cap before tokeniser
        if results:
            result = results[0]
            return SentimentResult(
                label=result["label"],
                confidence=round(float(result["score"]), 4),
            )
    except Exception as exc:
        logger.error("Sentiment inference failed: %s", exc)

    return SentimentResult(label="NEUTRAL", confidence=0.5)


def is_model_loaded() -> bool:
    """Return True if the sentiment model loaded successfully."""
    return _sentiment_pipeline is not None
