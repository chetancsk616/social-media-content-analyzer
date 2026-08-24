"""
Keyword extraction service using TF-IDF (scikit-learn).

For short texts (below the configured word threshold) the service falls back
to simple term-frequency ranking. This ensures useful keywords are always
returned even for a 3-sentence social-media caption.

No external API is used.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Common English stop-words (not social-media specific ones like hashtags/mentions)
_STOP_WORDS = "english"


def extract_keywords(text: str, n: int | None = None) -> List[str]:
    """
    Extract the most relevant keywords/phrases from social-media text.

    Args:
        text: Preprocessed post text.
        n: Number of keywords to return. Defaults to settings.keyword_count.

    Returns:
        List of keyword strings, ordered by relevance (most relevant first).
    """
    if n is None:
        n = settings.keyword_count

    words = _simple_tokenize(text)

    if len(words) < settings.tfidf_min_words:
        logger.debug("Text too short for TF-IDF (%d words); using frequency.", len(words))
        return _frequency_keywords(text, n)

    return _tfidf_keywords(text, n)


def _tfidf_keywords(text: str, n: int) -> List[str]:
    """
    Use TF-IDF on the post text to find important unigrams and bigrams.

    Because we have a single document, we treat each sentence as a
    mini-document so TF-IDF has variance to work with.
    """
    # Split into pseudo-documents (sentences) for IDF computation
    sentences = re.split(r"[.!?\n]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    if len(sentences) < 2:
        return _frequency_keywords(text, n)

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=_STOP_WORDS,
            max_features=200,
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Sum TF-IDF scores across all sentences
        scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        top_indices = scores.argsort()[::-1]

        keywords = []
        seen: set[str] = set()
        for idx in top_indices:
            kw = feature_names[idx]
            # Skip very short tokens or pure numeric tokens
            if len(kw) < 3 or kw.isdigit():
                continue
            # Avoid near-duplicate keywords (substrings of already-added ones)
            if any(kw in existing or existing in kw for existing in seen):
                continue
            keywords.append(kw)
            seen.add(kw)
            if len(keywords) >= n:
                break

        return keywords

    except Exception as exc:
        logger.warning("TF-IDF extraction failed: %s. Falling back.", exc)
        return _frequency_keywords(text, n)


def _frequency_keywords(text: str, n: int) -> List[str]:
    """Simple frequency-based keyword extraction for short texts."""
    # English stop words (minimal set)
    stop = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "shall", "can",
        "this", "that", "these", "those", "it", "its", "i", "we", "you",
        "he", "she", "they", "my", "your", "our", "their", "me", "him",
        "her", "us", "them", "what", "which", "who", "how", "when", "where",
        "not", "no", "if", "so", "as", "up", "out", "about",
    }
    words = _simple_tokenize(text)
    filtered = [w for w in words if w not in stop and len(w) >= 3 and not w.isdigit()]
    most_common = Counter(filtered).most_common(n)
    return [word for word, _ in most_common]


def _simple_tokenize(text: str) -> List[str]:
    """Lowercase word tokenisation preserving alphanumeric content."""
    return re.findall(r"[a-zA-Z][a-zA-Z0-9'-]*", text.lower())
