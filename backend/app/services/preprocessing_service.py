"""
Text preprocessing module for social-media content.

Goals:
  - Normalize whitespace and line endings without destroying structure.
  - Remove pathological repeated characters (e.g. "!!!!!!" → "!!!").
  - Preserve emojis, hashtags (#topic), mentions (@user), and URLs
    because these carry analytical meaning in social-media text.
  - Split into sentences and words for downstream analysis.
  - Return both a clean version and structured information.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List


# ── Compiled regex patterns ───────────────────────────────────────────────────

# Collapse 3+ consecutive identical characters to 2 (keeps "!!" but kills "!!!!!!")
_RE_REPEAT_CHARS = re.compile(r"(.)\1{3,}")

# Normalise multiple blank lines to at most two (one paragraph break)
_RE_MULTI_BLANK = re.compile(r"\n{3,}")

# Normalise horizontal whitespace (spaces/tabs) but keep newlines
_RE_HORIZ_SPACE = re.compile(r"[ \t]+")

# Simple sentence splitter: split on ". " / "? " / "! " / ".\n"
_RE_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Word tokeniser: letters, digits, apostrophes, hyphens inside words
_RE_WORD = re.compile(r"\b[\w''-]+\b", re.UNICODE)


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class PreprocessedText:
    raw: str
    clean: str
    sentences: List[str]
    words: List[str]
    paragraphs: List[str]


# ── Public API ────────────────────────────────────────────────────────────────

def preprocess(raw_text: str) -> PreprocessedText:
    """
    Clean and structure raw extracted text.

    Args:
        raw_text: Text as extracted from PDF or OCR.

    Returns:
        PreprocessedText with clean text, sentences, words, paragraphs.
    """
    text = raw_text

    # 1. Normalise unicode (NFC) — important for OCR output
    text = unicodedata.normalize("NFC", text)

    # 2. Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Collapse excessive repeated characters
    #    Keep up to 2 occurrences — "..." stays, "!!!!!!!" → "!!"
    text = _RE_REPEAT_CHARS.sub(lambda m: m.group(1) * 2, text)

    # 4. Normalise horizontal whitespace (tabs/multiple spaces → single space)
    text = _RE_HORIZ_SPACE.sub(" ", text)

    # 5. Trim each line individually
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # 6. Collapse 3+ blank lines to 2 (one paragraph separator)
    text = _RE_MULTI_BLANK.sub("\n\n", text)

    # 7. Strip leading/trailing whitespace from the full text
    text = text.strip()

    # Build structured outputs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = _split_sentences(text)
    words = _tokenize_words(text)

    return PreprocessedText(
        raw=raw_text,
        clean=text,
        sentences=sentences,
        words=words,
        paragraphs=paragraphs,
    )


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using regex (no NLTK dependency needed)."""
    parts = _RE_SENTENCE_SPLIT.split(text)
    return [s.strip() for s in parts if s.strip()]


def _tokenize_words(text: str) -> List[str]:
    """Extract word tokens (lowercase) from text."""
    return [m.group().lower() for m in _RE_WORD.finditer(text)]
