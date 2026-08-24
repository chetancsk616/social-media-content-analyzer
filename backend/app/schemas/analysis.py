"""
Pydantic schemas for request/response models.
All API responses are typed here — no arbitrary dicts in route handlers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Sub-models ────────────────────────────────────────────────────────────────

class SentimentResult(BaseModel):
    label: str = Field(..., description="POSITIVE or NEGATIVE")
    confidence: float = Field(..., ge=0.0, le=1.0)


class TextMetrics(BaseModel):
    word_count: int
    sentence_count: int
    avg_sentence_length: float = Field(..., description="Average words per sentence")
    avg_word_length: float = Field(..., description="Average characters per word")
    readability_score: float = Field(..., description="Flesch Reading Ease 0-100")
    readability_label: str = Field(..., description="Easy / Moderate / Difficult")
    paragraph_count: int


class ScoreBreakdown(BaseModel):
    hook: int = Field(..., ge=0, le=100)
    cta: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    readability: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    sentiment_score: int = Field(..., ge=0, le=100,
                                  description="Sentiment contribution 0-100")
    keyword_score: int = Field(..., ge=0, le=100)
    overall: int = Field(..., ge=0, le=100,
                          description="Weighted Engagement Optimization Score")


class HookAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=100)
    feedback: str


class CTAAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=100)
    feedback: str
    detected_phrases: List[str] = Field(default_factory=list)


class GeminiRecommendations(BaseModel):
    available: bool = True
    recommendations: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improved_post: Optional[str] = None
    alternative_hooks: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


# ── Top-level response ────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    filename: str
    file_type: str = Field(..., description="pdf | image | text")
    extraction_method: str = Field(
        ...,
        description="pymupdf | tesseract_ocr | direct_text"
    )
    extracted_text: str
    char_count: int

    sentiment: SentimentResult
    metrics: TextMetrics
    keywords: List[str]
    hashtags: List[str]

    hook_analysis: HookAnalysis
    cta_analysis: CTAAnalysis
    scores: ScoreBreakdown

    ai_recommendations: GeminiRecommendations


# ── Request models ────────────────────────────────────────────────────────────

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw social-media post text")
    platform: Optional[str] = Field(
        None, description="Optional platform hint: twitter/instagram/linkedin"
    )


# ── Health check ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    sentiment_model_loaded: bool
    gemini_configured: bool = False
    groq_configured: bool = False
    ai_configured: bool = False
