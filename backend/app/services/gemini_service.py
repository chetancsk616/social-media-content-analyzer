"""
AI Recommendation service using Groq API (with Gemini fallback).

Responsibilities:
  - Construct a structured prompt from local NLP analysis results.
  - Call the Groq API for blazing-fast inference.
  - Dynamically discover active Groq chat models on the account.
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
from typing import Optional, List

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
    """Call Groq API using official Groq client with dynamic active model discovery."""
    api_key_clean = api_key.strip()
    
    from groq import Groq
    client = Groq(api_key=api_key_clean, timeout=float(settings.groq_timeout_seconds))

    preferred_candidates = [
        settings.groq_model,
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "groq/compound",
        "groq/compound-mini",
        "allam-2-7b",
    ]

    models_to_try: List[str] = []

    # 1. First dynamically fetch live active models from Groq API
    try:
        remote_models = [
            m.id for m in client.models.list().data
            if not any(x in m.id for x in ["whisper", "guard", "audio", "orpheus"])
        ]
        # Order preferred candidates that exist remotely first
        for pref in preferred_candidates:
            if pref in remote_models:
                models_to_try.append(pref)
        # Append any remaining remote models
        for rm in remote_models:
            if rm not in models_to_try:
                models_to_try.append(rm)
    except Exception as exc:
        logger.warning("Could not dynamically query Groq models: %s", exc)
        models_to_try = [m for m in preferred_candidates if m]

    if not models_to_try:
        models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]

    last_error = None
    for model_name in models_to_try:
        try:
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional social media strategist. Respond ONLY with a valid JSON object matching the requested schema.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1500,
            )
            raw_text = chat_completion.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()
            return json.loads(raw_text)
        except Exception as model_err:
            last_error = model_err
            logger.info("Groq model %s failed: %s; trying next active model.", model_name, model_err)
            continue

    if last_error:
        raise last_error
    raise RuntimeError("All Groq models failed to produce a valid response.")


def _call_gemini_api(prompt: str, api_key: str) -> dict:
    """Fallback to Gemini API if configured."""
    import google.generativeai as genai

    genai.configure(api_key=api_key.strip())
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
