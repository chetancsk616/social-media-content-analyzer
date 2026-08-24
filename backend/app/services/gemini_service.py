"""
Gemini API integration service.

Responsibilities:
  - Construct a structured prompt from local analysis results.
  - Call the Gemini API (gemini-1.5-flash by default).
  - Parse the structured JSON response.
  - Handle ALL failure modes gracefully so the app still works without Gemini.

Used ONLY for:
  - Natural-language recommendations
  - Improved post rewriting
  - Strength/weakness summaries
  - Alternative hook suggestions

NOT used for: PDF extraction, OCR, sentiment, readability, keywords, scoring.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

from app.core.config import get_settings
from app.schemas.analysis import GeminiRecommendations

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_prompt(
    post_text: str,
    engagement_score: int,
    hook_score: int,
    cta_score: int,
    readability_score: int,
    sentiment_label: str,
    sentiment_confidence: float,
    keywords: list[str],
    clarity_score: int,
    structure_score: int,
) -> str:
    """Build the structured Gemini prompt."""
    analysis_json = json.dumps(
        {
            "post_text": post_text[:1500],  # Truncate very long posts
            "engagement_optimization_score": engagement_score,
            "hook_score": hook_score,
            "cta_score": cta_score,
            "readability_score": readability_score,
            "clarity_score": clarity_score,
            "structure_score": structure_score,
            "sentiment": {
                "label": sentiment_label,
                "confidence": sentiment_confidence,
            },
            "top_keywords": keywords,
        },
        ensure_ascii=False,
        indent=2,
    )

    return f"""You are an expert social-media content strategist.

You have received the following structured local analysis of a social-media post:

{analysis_json}

Based ONLY on the analysis data above, produce a JSON response with EXACTLY this structure:

{{
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2",
    "Actionable recommendation 3",
    "Actionable recommendation 4",
    "Actionable recommendation 5"
  ],
  "strengths": [
    "Strength 1",
    "Strength 2",
    "Strength 3"
  ],
  "weaknesses": [
    "Weakness 1",
    "Weakness 2",
    "Weakness 3"
  ],
  "improved_post": "A complete, improved rewrite of the post (preserve the core message, improve hook, add clear CTA, improve readability)",
  "alternative_hooks": [
    "Alternative hook option 1",
    "Alternative hook option 2",
    "Alternative hook option 3"
  ]
}}

Rules:
- Base every observation on the provided scores and keywords only.
- Do not invent facts not present in the post text.
- Keep recommendations specific and actionable (what to change and why).
- The improved post must be realistic for the detected platform type.
- Return ONLY the JSON object — no markdown, no preamble, no explanation.
"""


def generate_recommendations(
    post_text: str,
    engagement_score: int,
    hook_score: int,
    cta_score: int,
    readability_score: int,
    sentiment_label: str,
    sentiment_confidence: float,
    keywords: list[str],
    clarity_score: int,
    structure_score: int,
) -> GeminiRecommendations:
    """
    Call Gemini API to generate human-readable recommendations.

    Returns a GeminiRecommendations object. If Gemini is unavailable for
    any reason, returns a GeminiRecommendations with available=False
    and an appropriate error_message. The rest of the analysis is always
    displayed regardless.
    """
    api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        logger.warning("GEMINI_API_KEY not configured — skipping AI recommendations.")
        return GeminiRecommendations(
            available=False,
            error_message="AI recommendations unavailable: GEMINI_API_KEY not configured.",
        )

    prompt = _build_prompt(
        post_text=post_text,
        engagement_score=engagement_score,
        hook_score=hook_score,
        cta_score=cta_score,
        readability_score=readability_score,
        sentiment_label=sentiment_label,
        sentiment_confidence=sentiment_confidence,
        keywords=keywords,
        clarity_score=clarity_score,
        structure_score=structure_score,
    )

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1500,
            ),
            request_options={"timeout": settings.gemini_timeout_seconds},
        )

        raw_text = response.text.strip()

        # Strip markdown code fences if the model wraps the JSON
        if raw_text.startswith("```"):
            raw_text = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()

        data = json.loads(raw_text)

        return GeminiRecommendations(
            available=True,
            recommendations=data.get("recommendations", [])[:5],
            strengths=data.get("strengths", [])[:3],
            weaknesses=data.get("weaknesses", [])[:3],
            improved_post=data.get("improved_post"),
            alternative_hooks=data.get("alternative_hooks", [])[:3],
        )

    except json.JSONDecodeError as exc:
        logger.error("Gemini returned invalid JSON: %s", exc)
        return GeminiRecommendations(
            available=False,
            error_message="AI recommendations unavailable: Could not parse AI response.",
        )
    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        error_msg = str(exc)
        # Sanitise API-key-related messages
        if "api" in error_msg.lower() and "key" in error_msg.lower():
            error_msg = "Invalid or expired API key."
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            error_msg = "API rate limit reached. Try again in a moment."
        elif "timeout" in error_msg.lower():
            error_msg = "Request timed out. Try again."
        return GeminiRecommendations(
            available=False,
            error_message=f"AI recommendations temporarily unavailable: {error_msg}",
        )



