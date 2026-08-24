"""
Scoring service — deterministic heuristic algorithms for:

  1. Hook score        — quality of the opening lines
  2. CTA score         — presence and strength of a call-to-action
  3. Clarity score     — structural clarity and vocabulary complexity
  4. Structure score   — paragraph/sentence organisation
  5. Engagement score  — weighted composite of all sub-scores

ALL scoring is local. Gemini is not involved here.

Weights are defined in app/core/config.py and can be changed without
touching this file.
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass
from typing import List, Tuple

from app.schemas.analysis import HookAnalysis, CTAAnalysis, ScoreBreakdown
from app.core.config import get_settings

settings = get_settings()


# ──────────────────────────────────────────────────────────────────────────────
# Hook Scoring
# ──────────────────────────────────────────────────────────────────────────────

# Strong opening signals (weighted)
_HOOK_PATTERNS: List[Tuple[re.Pattern, int, str]] = [
    (re.compile(r"\?", re.I),                    15, "question"),
    (re.compile(r"^(what|how|why|who|when|where|did you|have you)", re.I), 10, "question_word"),
    (re.compile(r"\b(you|your)\b", re.I),         8,  "audience_address"),
    (re.compile(r"\b\d+\b"),                      10, "number_statistic"),
    (re.compile(r"(shocking|surprising|secret|truth|revealed|never|always|"
                r"most people|mistake|warning|stop|start|finally|proven|"
                r"science|research|study)", re.I), 12, "power_word"),
    (re.compile(r"^(imagine|picture|think about|what if)", re.I), 10, "imagination"),
    (re.compile(r"(free|save|win|earn|lose|boost|grow|skyrocket|explode)", re.I), 6, "benefit"),
    (re.compile(r"^(i |we )", re.I),             -5, "self_start_penalty"),
    (re.compile(r"(today|right now|in \d+ days?|just \d+ minutes?)", re.I), 5, "urgency"),
]

# Generic filler phrases that weaken a hook
_FILLER_PATTERNS = [
    "hello everyone", "hi there", "good morning", "happy monday",
    "happy to share", "excited to announce", "i am pleased",
    "just wanted to say", "greetings", "dear followers",
]


def analyze_hook(text: str, sentences: List[str]) -> HookAnalysis:
    """
    Score the quality of the opening hook.

    Analyses the first 1-2 sentences (or first 200 characters).
    Returns a score 0-100 and descriptive feedback.
    """
    if not sentences:
        return HookAnalysis(score=0, feedback="No text found to analyse.")

    # Take the first 1-2 sentences as the hook
    hook_text = " ".join(sentences[:2])[:300]
    hook_lower = hook_text.lower()

    score = 40  # Base score — a blank post starts here
    reasons: List[str] = []
    penalties: List[str] = []

    # Check filler phrases
    for filler in _FILLER_PATTERNS:
        if filler in hook_lower:
            score -= 20
            penalties.append("generic opening phrase")
            break

    # Evaluate patterns
    matched_labels: set[str] = set()
    for pattern, weight, label in _HOOK_PATTERNS:
        if pattern.search(hook_text):
            if label not in matched_labels:
                score += weight
                matched_labels.add(label)
                if weight > 0:
                    reasons.append(label.replace("_", " "))

    # Reward brevity (≤15 words is punchy)
    hook_words = len(hook_text.split())
    if hook_words <= 15:
        score += 5
        reasons.append("concise opening")
    elif hook_words > 40:
        score -= 8
        penalties.append("opening is too long")

    # Clamp
    score = max(0, min(100, score))

    # Build feedback
    if score >= 80:
        feedback = "Strong opening hook. " + ("Strengths: " + ", ".join(reasons) + "." if reasons else "")
    elif score >= 60:
        feedback = "Decent hook with room to improve. "
        if reasons:
            feedback += "Works well: " + ", ".join(reasons) + ". "
        if penalties:
            feedback += "Issues: " + ", ".join(penalties) + "."
    elif score >= 40:
        feedback = "The hook is weak. Consider starting with a question, statistic, or strong benefit statement."
        if penalties:
            feedback += " Avoid: " + ", ".join(penalties) + "."
    else:
        feedback = "Very weak opening. Start with something that immediately grabs attention — a bold claim, a question, or a surprising fact."

    return HookAnalysis(score=score, feedback=feedback.strip())


# ──────────────────────────────────────────────────────────────────────────────
# CTA Scoring
# ──────────────────────────────────────────────────────────────────────────────

# Ordered by strength (higher weight = stronger CTA)
_CTA_PATTERNS: List[Tuple[re.Pattern, int]] = [
    # Direct imperatives with target action
    (re.compile(r"\b(buy|order|purchase|sign up|register|join|subscribe|download)\b", re.I), 30),
    (re.compile(r"\b(book|claim|get started|try|start|apply|enroll|enrol)\b", re.I), 25),
    (re.compile(r"\b(comment|reply|respond|tell us|let us know|share your|dm|message)\b", re.I), 22),
    (re.compile(r"\b(share|retweet|repost|tag|mention|forward)\b", re.I), 20),
    (re.compile(r"\b(click|tap|swipe|visit|check out|read|watch|listen)\b", re.I), 18),
    (re.compile(r"\b(like|follow|save|pin|bookmark|favourite|favorite)\b", re.I), 15),
    (re.compile(r"\b(learn more|find out|discover|explore|see how)\b", re.I), 18),
    (re.compile(r"(link in bio|link below|link in profile|bio link)", re.I), 15),
    (re.compile(r"\?$", re.M),                                              8),  # question at end
    (re.compile(r"\b(today|now|limited|last chance|don't miss|ends soon|hurry)\b", re.I), 10),  # urgency
]


def analyze_cta(text: str, sentences: List[str]) -> CTAAnalysis:
    """
    Detect and score the call-to-action in the post.

    Returns score 0-100, descriptive feedback, and detected CTA phrases.
    """
    if not text.strip():
        return CTAAnalysis(score=0, feedback="No text to analyse.", detected_phrases=[])

    score = 0
    detected: List[str] = []
    matched_labels: set[int] = set()  # track pattern index to avoid double-counting

    for i, (pattern, weight) in enumerate(_CTA_PATTERNS):
        match = pattern.search(text)
        if match and i not in matched_labels:
            score += weight
            detected.append(match.group().strip())
            matched_labels.add(i)

    score = max(0, min(100, score))

    # Feedback based on score band
    if score >= 81:
        feedback = "Strong CTA — the post clearly directs the audience to take action."
    elif score >= 61:
        feedback = "Good CTA. Consider adding urgency or a more specific action to strengthen it."
    elif score >= 31:
        feedback = "Moderate CTA. The post hints at action but is not explicit. Try a direct command such as 'Comment below' or 'Click the link in bio'."
    else:
        feedback = "Weak or missing CTA. Add a clear call-to-action to drive engagement."

    return CTAAnalysis(score=score, feedback=feedback, detected_phrases=list(set(detected)))


# ──────────────────────────────────────────────────────────────────────────────
# Clarity Scoring
# ──────────────────────────────────────────────────────────────────────────────

def compute_clarity_score(
    text: str,
    words: List[str],
    sentences: List[str],
    paragraphs: List[str],
) -> int:
    """
    Heuristic content-clarity score (0-100).

    Evaluates:
    - Sentence length consistency
    - Excessive ALL CAPS
    - Excessive punctuation marks
    - Vocabulary complexity (long words)
    - Repetition
    - Paragraph organisation
    """
    if not text or not words:
        return 0

    score = 100  # Start perfect and deduct

    # ── Sentence length ───────────────────────────────────────────────────────
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        # Penalise very long sentences (>30 words avg)
        if avg_len > 30:
            score -= min(20, int((avg_len - 30) * 1.5))
        # Penalise very short sentences (may indicate fragmented thoughts)
        elif avg_len < 5 and len(sentences) > 3:
            score -= 10

    # ── Excessive ALL CAPS ────────────────────────────────────────────────────
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
    caps_ratio = caps_words / max(len(words), 1)
    if caps_ratio > 0.3:
        score -= min(35, int(caps_ratio * 50))

    # ── Excessive punctuation ─────────────────────────────────────────────────
    exclamation_count = text.count("!")
    if exclamation_count > 5:
        score -= min(15, exclamation_count - 5)

    # ── Vocabulary complexity ─────────────────────────────────────────────────
    # Words with > 3 syllables (rough proxy) — too many = hard to read
    complex_words = [w for w in words if len(w) > 10]
    complex_ratio = len(complex_words) / max(len(words), 1)
    if complex_ratio > 0.25:
        score -= min(15, int((complex_ratio - 0.25) * 60))

    # ── Repetition ────────────────────────────────────────────────────────────
    from collections import Counter
    word_counts = Counter(w.lower() for w in words if len(w) > 4)
    if word_counts:
        most_common_count = word_counts.most_common(1)[0][1]
        repetition_ratio = most_common_count / max(len(words), 1)
        if repetition_ratio > 0.1:
            score -= min(10, int((repetition_ratio - 0.1) * 50))

    # ── Paragraph organisation ────────────────────────────────────────────────
    if len(paragraphs) >= 2:
        score += 5  # reward for breaking into paragraphs

    return max(0, min(100, score))


# ──────────────────────────────────────────────────────────────────────────────
# Structure Scoring
# ──────────────────────────────────────────────────────────────────────────────

def compute_structure_score(
    text: str,
    sentences: List[str],
    paragraphs: List[str],
) -> int:
    """
    Score the structural organisation of the post (0-100).
    """
    score = 50  # Base

    # Has multiple paragraphs
    if len(paragraphs) >= 2:
        score += 15
    if len(paragraphs) >= 3:
        score += 10

    # Has a reasonable number of sentences per paragraph
    if sentences:
        score += 10

    # Uses line breaks or formatting
    if "\n" in text:
        score += 5

    # Has hashtags (structural social element)
    if re.search(r"#\w+", text):
        score += 5

    # Has emojis (visual structure)
    emoji_count = len(re.findall(
        r"[\U0001F300-\U0001F9FF\U00002702-\U000027B0]", text
    ))
    if 1 <= emoji_count <= 10:
        score += 5
    elif emoji_count > 15:
        score -= 5  # emoji overload

    return max(0, min(100, score))


# ──────────────────────────────────────────────────────────────────────────────
# Sentiment → 0-100 contribution
# ──────────────────────────────────────────────────────────────────────────────

def sentiment_to_score(label: str, confidence: float) -> int:
    """Convert sentiment label + confidence to a 0-100 engagement score."""
    # For social media, positive sentiment with high confidence is best.
    # Negative with high confidence can still be engaging (controversial content)
    # but we treat neutral as lower.
    if label == "POSITIVE":
        return int(60 + confidence * 40)
    elif label == "NEGATIVE":
        # Negative can be engaging (calls to action against something)
        return int(40 + confidence * 30)
    else:
        # NEUTRAL
        return 50


# ──────────────────────────────────────────────────────────────────────────────
# Keyword richness → 0-100 contribution
# ──────────────────────────────────────────────────────────────────────────────

def keyword_richness_score(keywords: List[str], word_count: int) -> int:
    """
    Score keyword richness: having varied, meaningful keywords is a positive signal.
    """
    n = len(keywords)
    if n == 0:
        return 20
    if n >= 8:
        base = 85
    elif n >= 5:
        base = 70
    elif n >= 3:
        base = 55
    else:
        base = 35

    # Bonus for longer keywords (multi-word = more specific)
    multi_word = sum(1 for kw in keywords if " " in kw)
    base += min(15, multi_word * 5)

    return min(100, base)


# ──────────────────────────────────────────────────────────────────────────────
# Weighted Engagement Score
# ──────────────────────────────────────────────────────────────────────────────

def compute_engagement_score(
    hook_score: int,
    cta_score: int,
    readability_score: int,
    clarity_score: int,
    sentiment_score: int,
    keyword_score: int,
    structure_score: int,
) -> int:
    """
    Compute the overall Engagement Optimization Score (0-100).

    This is a heuristic weighted average — NOT a scientifically validated
    prediction of actual social-media engagement.

    Weights are defined in app/core/config.py.
    """
    weights = settings.scoring_weights

    raw = (
        hook_score       * weights["hook"]
        + cta_score      * weights["cta"]
        + readability_score * weights["readability"]
        + clarity_score  * weights["clarity"]
        + sentiment_score * weights["sentiment"]
        + keyword_score  * weights["keywords"]
        + structure_score * weights["structure"]
    )

    # Clamp to [0, 100]
    return max(0, min(100, round(raw)))


def build_score_breakdown(
    hook: int,
    cta: int,
    readability_100: int,
    clarity: int,
    sentiment_score: int,
    keyword_score: int,
    structure: int,
) -> ScoreBreakdown:
    overall = compute_engagement_score(
        hook_score=hook,
        cta_score=cta,
        readability_score=readability_100,
        clarity_score=clarity,
        sentiment_score=sentiment_score,
        keyword_score=keyword_score,
        structure_score=structure,
    )

    return ScoreBreakdown(
        hook=hook,
        cta=cta,
        clarity=clarity,
        readability=readability_100,
        structure=structure,
        sentiment_score=sentiment_score,
        keyword_score=keyword_score,
        overall=overall,
    )
