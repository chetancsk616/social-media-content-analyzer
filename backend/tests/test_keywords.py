"""Tests for keyword extraction service."""

import pytest
from app.services.keyword_service import extract_keywords, _frequency_keywords


def test_extract_keywords_normal_text():
    text = """
    Artificial intelligence is transforming the way we work and live.
    Machine learning algorithms are being applied to healthcare, finance,
    and transportation. Deep learning models can now understand images,
    text, and speech with remarkable accuracy. The future of technology
    looks exciting with AI-driven innovations across every industry.
    """
    keywords = extract_keywords(text)
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert len(keywords) <= 10


def test_extract_keywords_short_text():
    # Short text should use frequency fallback
    text = "AI technology innovation"
    keywords = extract_keywords(text, n=5)
    assert isinstance(keywords, list)
    # May return fewer than 5 for very short text


def test_extract_keywords_empty_text():
    keywords = extract_keywords("")
    assert isinstance(keywords, list)


def test_frequency_keywords_basic():
    text = "technology technology technology innovation innovation marketing"
    kws = _frequency_keywords(text, 3)
    assert "technology" in kws
    assert len(kws) <= 3


def test_keywords_no_stop_words():
    text = "the and or but in on at to for of with by from is are was were"
    keywords = extract_keywords(text, n=5)
    # Stop words should be filtered out
    for kw in keywords:
        assert kw not in {"the", "and", "or", "but", "in"}


def test_keywords_count_limit():
    text = " ".join(["word" + str(i) for i in range(100)])
    keywords = extract_keywords(text, n=5)
    assert len(keywords) <= 5
