"""
Centralized configuration for the Social Media Content Analyzer backend.
Scoring weights and application settings are defined here so they can be
modified in one place without touching business logic.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    # ── Application ────────────────────────────────────────────────────────────
    app_name: str = "Social Media Content Analyzer"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── CORS ───────────────────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:5173"

    # ── File upload constraints ─────────────────────────────────────────────────
    max_file_size_mb: int = 10
    allowed_extensions: tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg")
    allowed_mime_types: tuple[str, ...] = (
        "application/pdf",
        "image/png",
        "image/jpeg",
    )

    # ── NLP / Model ────────────────────────────────────────────────────────────
    sentiment_model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    # Minimum number of words for full TF-IDF to kick in; below this we use
    # frequency-based extraction.
    tfidf_min_words: int = 20
    # Number of keywords to return
    keyword_count: int = 8

    # ── External AI ────────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_timeout_seconds: int = 30

    # ── Scoring weights (must sum to 1.0) ──────────────────────────────────────
    # These weights are applied in the engagement scoring engine.
    scoring_weights: Dict[str, float] = {
        "hook": 0.25,        # First impression / opening hook
        "cta": 0.20,         # Call-to-action strength
        "readability": 0.15, # How easy the text is to read
        "clarity": 0.15,     # Content clarity / organisation
        "sentiment": 0.10,   # Sentiment / tone suitability
        "keywords": 0.10,    # Keyword relevance / richness
        "structure": 0.05,   # Content structure quality
    }

    # ── OCR ───────────────────────────────────────────────────────────────────
    # If a PDF page yields fewer than this many characters, treat it as scanned.
    ocr_text_threshold: int = 50
    tesseract_config: str = "--oem 3 --psm 6"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
