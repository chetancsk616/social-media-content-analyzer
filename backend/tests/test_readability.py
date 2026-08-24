"""Tests for readability calculations."""

import pytest
from app.services.readability_service import (
    compute_readability_metrics,
    readability_score_to_100,
    _count_syllables,
    _readability_label,
)


def test_syllable_counting():
    assert _count_syllables("the") == 1
    assert _count_syllables("beautiful") >= 3
    assert _count_syllables("ai") >= 1
    assert _count_syllables("") == 0


def test_readability_metrics_basic():
    text = "This is a simple post. It has short sentences. Easy to read content here."
    paragraphs = [text]
    metrics = compute_readability_metrics(text, paragraphs)

    assert metrics.word_count > 0
    assert metrics.sentence_count > 0
    assert metrics.avg_sentence_length > 0
    assert 0 <= metrics.readability_score <= 100


def test_readability_empty_text():
    metrics = compute_readability_metrics("", [])
    assert metrics.word_count == 0
    assert metrics.sentence_count >= 1  # max(0, 1)


def test_readability_label_easy():
    assert _readability_label(90) == "Easy"


def test_readability_label_moderate():
    assert _readability_label(65) == "Moderate"


def test_readability_label_difficult():
    assert _readability_label(25) == "Difficult"


def test_readability_score_to_100():
    # Scores in the ideal range (60-80 Flesch) should give high 0-100 scores
    score = readability_score_to_100(70)
    assert score >= 80

    score = readability_score_to_100(30)
    assert score < 80


def test_readability_metrics_multi_paragraph():
    text = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
    paragraphs = text.split("\n\n")
    metrics = compute_readability_metrics(text, paragraphs)
    assert metrics.paragraph_count == 3
