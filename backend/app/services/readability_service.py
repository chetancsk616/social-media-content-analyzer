"""
Readability analysis service.

Implements Flesch Reading Ease locally — no external API.

Flesch Reading Ease formula:
    score = 206.835
            - 1.015  * (total_words / total_sentences)
            - 84.6   * (total_syllables / total_words)

Score interpretation:
    90–100   Very Easy
    80–89    Easy
    70–79    Fairly Easy
    60–69    Standard / Moderate
    50–59    Fairly Difficult
    30–49    Difficult
    0–29     Very Difficult

We also compute complementary metrics (word count, sentence length, etc.)
that are shown in the dashboard.
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass
from typing import List

from app.schemas.analysis import TextMetrics


# ── Syllable counting ─────────────────────────────────────────────────────────

_VOWELS = re.compile(r"[aeiouyAEIOUY]+")
_SILENT_E = re.compile(r"[^aeiou]e$", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    """Estimate syllable count for an English word."""
    word = word.strip().lower()
    if not word:
        return 0

    # Remove non-alpha
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 1

    count = len(_VOWELS.findall(word))

    # Subtract silent 'e' at word end
    if _SILENT_E.search(word) and count > 1:
        count -= 1

    return max(1, count)


# ── Sentence and word utilities ───────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def _split_words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z''-]+", text)


# ── Flesch Reading Ease ───────────────────────────────────────────────────────

def _flesch_reading_ease(words: List[str], sentences: List[str]) -> float:
    """Return Flesch Reading Ease score (0–100)."""
    n_words = len(words)
    n_sentences = len(sentences)

    if n_words == 0 or n_sentences == 0:
        return 50.0  # neutral fallback

    total_syllables = sum(_count_syllables(w) for w in words)

    score = (
        206.835
        - 1.015 * (n_words / n_sentences)
        - 84.6 * (total_syllables / n_words)
    )
    return max(0.0, min(100.0, score))


def _readability_label(score: float) -> str:
    if score >= 80:
        return "Easy"
    elif score >= 60:
        return "Moderate"
    elif score >= 40:
        return "Fairly Difficult"
    else:
        return "Difficult"


# ── Public API ────────────────────────────────────────────────────────────────

def compute_readability_metrics(text: str, paragraphs: List[str]) -> TextMetrics:
    """
    Compute all readability and structural metrics for the given text.

    Args:
        text: Preprocessed clean text.
        paragraphs: List of paragraphs (already split by preprocessor).

    Returns:
        TextMetrics Pydantic model.
    """
    words = _split_words(text)
    sentences = _split_sentences(text)

    n_words = len(words)
    n_sentences = max(len(sentences), 1)
    n_paragraphs = max(len(paragraphs), 1)

    avg_sentence_length = round(n_words / n_sentences, 2)
    avg_word_length = round(
        sum(len(w) for w in words) / max(n_words, 1), 2
    )

    flesch = _flesch_reading_ease(words, sentences)
    flesch_rounded = round(flesch, 1)

    return TextMetrics(
        word_count=n_words,
        sentence_count=n_sentences,
        avg_sentence_length=avg_sentence_length,
        avg_word_length=avg_word_length,
        readability_score=flesch_rounded,
        readability_label=_readability_label(flesch),
        paragraph_count=n_paragraphs,
    )


def readability_score_to_100(flesch_score: float) -> int:
    """
    Convert a Flesch Reading Ease score (0-100, higher=easier) to a
    0-100 engagement-friendly readability score.

    For social media, very high Flesch (very easy) is good up to a point.
    We reward the 60-80 range most, penalise extremes mildly.
    """
    # Clamp
    score = max(0.0, min(100.0, flesch_score))

    # Map: 60-80 → ~85-100, outside → tapers off
    if 60 <= score <= 80:
        return int(85 + (score - 60) * 0.75)
    elif score > 80:
        # Very easy — slight penalty for potential oversimplification
        return int(100 - (score - 80) * 0.5)
    else:
        # Difficult — bigger penalty
        return int(max(0, 85 - (60 - score) * 1.5))
