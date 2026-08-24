"""
AI Recommendation service using Groq API (with Gemini fallback).

Responsibilities:
  - Construct a structured prompt from local NLP analysis results.
  - Call the Groq API (llama-3.3-70b-versatile or llama-3.1-8b-instant) for blazing-fast inference.
  - Parse the structured JSON response.
  - Handle ALL failure modes gracefully so the app still works without an AI key.

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

import httpx

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
    """Build the structured prompt for LLM."""
    analysis_json = json.dumps(
        {
            "post_text": post_text[:1500],
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
- The improved post must be realistic for social media.
- Return ONLY the raw JSON object — no markdown, no explanation."""


def _call_groq_api(prompt: str, api_key: str) -> dict:
    """Call Groq API using HTTP client with JSON mode."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model or "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional social media content analyst. You always respond in valid JSON matching the requested schema.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 1500,
    }

    with httpx.Client(timeout=settings.groq_timeout_seconds) as client:
        response = client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return json.loads(content)


def _call_gemini_api(prompt: str, api_key: str) -> dict:
    """Fallback to Gemini API if configured."""
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
    if raw_text.startswith("```"):
        raw_text = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()

    return json.loads(raw_text)


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
    Generate human-readable AI recommendations using Groq API (or Gemini fallback).
    """
    groq_key = settings.groq_api_key or os.environ.get("GROQ_API_KEY", "")
    gemini_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    if not groq_key and not gemini_key:
        logger.info("Neither GROQ_API_KEY nor GEMINI_API_KEY configured — skipping AI recommendations.")
        return GeminiRecommendations(
            available=False,
            error_message="AI recommendations unavailable: GROQ_API_KEY not configured.",
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

    # 1. Try Groq API first
    if groq_key:
        try:
            data = _call_groq_api(prompt, groq_key)
            return GeminiRecommendations(
                available=True,
                recommendations=data.get("recommendations", [])[:5],
                strengths=data.get("strengths", [])[:3],
                weaknesses=data.get("weaknesses", [])[:3],
                improved_post=data.get("improved_post"),
                alternative_hooks=data.get("alternative_hooks", [])[:3],
            )
        except Exception as exc:
            logger.error("Groq API call failed: %s", exc)
            if not gemini_key:
                return GeminiRecommendations(
                    available=False,
                    error_message=f"AI recommendations temporarily unavailable: {exc}",
                )

    # 2. Try Gemini API fallback
    if gemini_key:
        try:
            data = _call_gemini_api(prompt, gemini_key)
            return GeminiRecommendations(
                available=True,
                recommendations=data.get("recommendations", [])[:5],
                strengths=data.get("strengths", [])[:3],
                weaknesses=data.get("weaknesses", [])[:3],
                improved_post=data.get("improved_post"),
                alternative_hooks=data.get("alternative_hooks", [])[:3],
            )
        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            return GeminiRecommendations(
                available=False,
                error_message=f"AI recommendations temporarily unavailable: {exc}",
            )

    return GeminiRecommendations(
        available=False,
        error_message="AI recommendations unavailable: No valid API response.",
    )
