"""
Analysis orchestrator — combines all services into a single pipeline.

This module is the only one that knows about all other services.
Route handlers call `run_analysis()` and receive a complete AnalysisResponse.

Pipeline:
    File/Text → Extraction → Preprocessing → NLP → Scoring → Gemini → Response
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import get_settings
from app.schemas.analysis import AnalysisResponse
from app.services import (
    pdf_service,
    ocr_service,
    preprocessing_service,
    sentiment_service,
    keyword_service,
    readability_service,
    scoring_service,
    hashtag_service,
    gemini_service,
)

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


async def run_analysis_on_file(file: UploadFile) -> AnalysisResponse:
    """
    Full pipeline for uploaded file (PDF or image).

    1. Validate file.
    2. Save to a secure temp file.
    3. Extract text.
    4. Run NLP pipeline.
    5. Generate AI recommendations.
    6. Return structured response.
    """
    # ── Validate ──────────────────────────────────────────────────────────────
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content_type = (file.content_type or "").split(";")[0].lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported MIME type '{content_type}'. Upload a PDF or image."
        )

    # ── Read and check size ───────────────────────────────────────────────────
    file_bytes = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    if len(file_bytes) == 0:
        raise ValueError("The uploaded file is empty.")

    if len(file_bytes) > max_bytes:
        raise ValueError(
            f"File exceeds the maximum size of {settings.max_file_size_mb} MB."
        )

    # ── Write to secure temp file ─────────────────────────────────────────────
    tmp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = Path(tmp.name)

        # ── Extract text ──────────────────────────────────────────────────────
        if suffix == ".pdf":
            raw_text, extraction_method = pdf_service.extract_text_from_pdf(
                tmp_path
            )
            file_type = "pdf"
        else:
            raw_text = ocr_service.ocr_image_file(str(tmp_path))
            extraction_method = "tesseract_ocr"
            file_type = "image"

    finally:
        # Always clean up temp file
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass

    return await _run_nlp_pipeline(
        text=raw_text,
        filename=file.filename or "uploaded_file",
        file_type=file_type,
        extraction_method=extraction_method,
    )


async def run_analysis_on_text(text: str) -> AnalysisResponse:
    """Pipeline for direct text input (no file upload)."""
    if not text.strip():
        raise ValueError("The provided text is empty.")

    return await _run_nlp_pipeline(
        text=text,
        filename="text_input",
        file_type="text",
        extraction_method="direct_text",
    )


async def _run_nlp_pipeline(
    text: str,
    filename: str,
    file_type: str,
    extraction_method: str,
) -> AnalysisResponse:
    """
    Shared NLP analysis pipeline used by both file and text endpoints.
    """
    # ── 1. Preprocess ─────────────────────────────────────────────────────────
    preprocessed = preprocessing_service.preprocess(text)

    if not preprocessed.clean.strip():
        raise ValueError(
            "No readable text could be extracted from this content. "
            "Please check the file quality."
        )

    # ── 2. Sentiment (DistilBERT) ─────────────────────────────────────────────
    sentiment = sentiment_service.analyze_sentiment(preprocessed.clean)

    # ── 3. Keywords (TF-IDF) ─────────────────────────────────────────────────
    keywords = keyword_service.extract_keywords(preprocessed.clean)

    # ── 4. Readability ────────────────────────────────────────────────────────
    metrics = readability_service.compute_readability_metrics(
        preprocessed.clean, preprocessed.paragraphs
    )
    readability_100 = readability_service.readability_score_to_100(
        metrics.readability_score
    )

    # ── 5. Hook analysis ──────────────────────────────────────────────────────
    hook_analysis = scoring_service.analyze_hook(
        preprocessed.clean, preprocessed.sentences
    )

    # ── 6. CTA analysis ──────────────────────────────────────────────────────
    cta_analysis = scoring_service.analyze_cta(
        preprocessed.clean, preprocessed.sentences
    )

    # ── 7. Clarity & Structure ────────────────────────────────────────────────
    clarity_score = scoring_service.compute_clarity_score(
        preprocessed.clean,
        preprocessed.words,
        preprocessed.sentences,
        preprocessed.paragraphs,
    )

    structure_score = scoring_service.compute_structure_score(
        preprocessed.clean,
        preprocessed.sentences,
        preprocessed.paragraphs,
    )

    # ── 8. Sentiment & keyword contribution ──────────────────────────────────
    sentiment_score = scoring_service.sentiment_to_score(
        sentiment.label, sentiment.confidence
    )
    keyword_score = scoring_service.keyword_richness_score(
        keywords, metrics.word_count
    )

    # ── 9. Engagement score (weighted) ────────────────────────────────────────
    scores = scoring_service.build_score_breakdown(
        hook=hook_analysis.score,
        cta=cta_analysis.score,
        readability_100=readability_100,
        clarity=clarity_score,
        sentiment_score=sentiment_score,
        keyword_score=keyword_score,
        structure=structure_score,
    )

    # ── 10. Hashtag suggestions ───────────────────────────────────────────────
    hashtags = hashtag_service.generate_hashtags(keywords, preprocessed.clean)

    # ── 11. Gemini recommendations ────────────────────────────────────────────
    ai_recommendations = gemini_service.generate_recommendations(
        post_text=preprocessed.clean,
        engagement_score=scores.overall,
        hook_score=scores.hook,
        cta_score=scores.cta,
        readability_score=scores.readability,
        sentiment_label=sentiment.label,
        sentiment_confidence=sentiment.confidence,
        keywords=keywords,
        clarity_score=scores.clarity,
        structure_score=scores.structure,
    )

    return AnalysisResponse(
        filename=filename,
        file_type=file_type,
        extraction_method=extraction_method,
        extracted_text=preprocessed.clean,
        char_count=len(preprocessed.clean),
        sentiment=sentiment,
        metrics=metrics,
        keywords=keywords,
        hashtags=hashtags,
        hook_analysis=hook_analysis,
        cta_analysis=cta_analysis,
        scores=scores,
        ai_recommendations=ai_recommendations,
    )
