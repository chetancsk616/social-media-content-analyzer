"""Tests for the scoring service (hook, CTA, clarity, engagement)."""

import pytest
from app.services.scoring_service import (
    analyze_hook,
    analyze_cta,
    compute_clarity_score,
    compute_engagement_score,
    build_score_breakdown,
    sentiment_to_score,
    keyword_richness_score,
)


# ── Hook tests ────────────────────────────────────────────────────────────────

def test_hook_with_question():
    hook = analyze_hook("Did you know 90% of people fail at this?", ["Did you know 90% of people fail at this?"])
    assert hook.score > 50
    assert hook.feedback


def test_hook_with_filler():
    hook = analyze_hook("Hello everyone! Just wanted to share this.", ["Hello everyone! Just wanted to share this."])
    assert hook.score < 50


def test_hook_empty_text():
    hook = analyze_hook("", [])
    assert hook.score == 0


def test_hook_with_statistic():
    hook = analyze_hook("5 ways to double your productivity today.", ["5 ways to double your productivity today."])
    assert hook.score > 40


# ── CTA tests ─────────────────────────────────────────────────────────────────

def test_cta_with_strong_action():
    cta = analyze_cta("Click the link below and download your free guide today!", ["Click the link below and download your free guide today!"])
    assert cta.score > 60
    assert len(cta.detected_phrases) > 0


def test_cta_with_no_action():
    cta = analyze_cta("The weather was nice yesterday.", ["The weather was nice yesterday."])
    assert cta.score < 30


def test_cta_with_comment():
    cta = analyze_cta("Comment below with your thoughts!", ["Comment below with your thoughts!"])
    assert cta.score >= 15


def test_cta_empty():
    cta = analyze_cta("", [])
    assert cta.score == 0


# ── Clarity tests ─────────────────────────────────────────────────────────────

def test_clarity_normal_text():
    text = "This is a clear and concise post about technology and innovation."
    words = text.split()
    sentences = [text]
    paragraphs = [text]
    score = compute_clarity_score(text, words, sentences, paragraphs)
    assert 0 <= score <= 100


def test_clarity_all_caps_penalty():
    text = "THIS IS ALL CAPS AND VERY LOUD AND AGGRESSIVE POST CONTENT HERE"
    words = text.split()
    sentences = [text]
    paragraphs = [text]
    score = compute_clarity_score(text, words, sentences, paragraphs)
    assert score < 80


# ── Engagement score tests ────────────────────────────────────────────────────

def test_engagement_score_range():
    score = compute_engagement_score(
        hook_score=80,
        cta_score=70,
        readability_score=75,
        clarity_score=85,
        sentiment_score=80,
        keyword_score=70,
        structure_score=75,
    )
    assert 0 <= score <= 100


def test_engagement_score_all_zeros():
    score = compute_engagement_score(0, 0, 0, 0, 0, 0, 0)
    assert score == 0


def test_engagement_score_all_max():
    score = compute_engagement_score(100, 100, 100, 100, 100, 100, 100)
    assert score == 100


def test_sentiment_to_score_positive():
    score = sentiment_to_score("POSITIVE", 0.95)
    assert score >= 85


def test_sentiment_to_score_neutral():
    score = sentiment_to_score("NEUTRAL", 0.5)
    assert score == 50


def test_keyword_richness_no_keywords():
    score = keyword_richness_score([], 100)
    assert score == 20


def test_keyword_richness_good_keywords():
    score = keyword_richness_score(["ai", "machine learning", "technology", "innovation", "data", "science", "automation", "deep learning"], 200)
    assert score >= 80
