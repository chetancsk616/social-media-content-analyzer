"""
Hashtag suggestion service.

Generates relevant hashtag suggestions from:
  1. TF-IDF keywords (already extracted)
  2. Noun phrases detected via simple regex patterns
  3. Domain/topic normalisation

No social-media API is used.
"""

from __future__ import annotations

import re
from typing import List


# Prefix mapping: common topics → canonical hashtag variants
_DOMAIN_MAP: dict[str, str] = {
    "artificial intelligence": "ArtificialIntelligence",
    "machine learning": "MachineLearning",
    "deep learning": "DeepLearning",
    "social media": "SocialMedia",
    "content marketing": "ContentMarketing",
    "digital marketing": "DigitalMarketing",
    "personal development": "PersonalDevelopment",
    "mental health": "MentalHealth",
    "small business": "SmallBusiness",
    "remote work": "RemoteWork",
    "work from home": "WorkFromHome",
    "entrepreneurship": "Entrepreneurship",
    "data science": "DataScience",
    "natural language": "NLP",
    "computer vision": "ComputerVision",
    "cloud computing": "CloudComputing",
    "software engineering": "SoftwareEngineering",
}


def _to_hashtag(phrase: str) -> str:
    """Convert a phrase or keyword into CamelCase hashtag format."""
    phrase = phrase.strip().lower()

    # Check domain map first
    if phrase in _DOMAIN_MAP:
        return "#" + _DOMAIN_MAP[phrase]

    # CamelCase conversion: capitalise each word
    words = re.sub(r"[^a-zA-Z0-9\s]", "", phrase).split()
    if not words:
        return ""

    return "#" + "".join(w.capitalize() for w in words)


def generate_hashtags(keywords: List[str], text: str, n: int = 8) -> List[str]:
    """
    Generate hashtag suggestions from keywords and text content.

    Args:
        keywords: Keywords extracted by keyword_service.
        text: Original post text (for noun-phrase detection).
        n: Maximum number of hashtags to return.

    Returns:
        List of hashtag strings e.g. ['#MachineLearning', '#Technology'].
    """
    seen: set[str] = set()
    hashtags: List[str] = []

    # 1. Convert keywords to hashtags
    for kw in keywords:
        tag = _to_hashtag(kw)
        if tag and tag not in seen and len(tag) > 2:
            seen.add(tag)
            hashtags.append(tag)

    # 2. Extract existing hashtags from the text and include them
    existing = re.findall(r"#(\w+)", text)
    for h in existing:
        tag = "#" + h
        if tag not in seen:
            seen.add(tag)
            hashtags.append(tag)

    # 3. Extract simple noun phrases from text (Adj? Noun patterns via regex)
    noun_phrases = _extract_noun_phrases(text)
    for np in noun_phrases:
        tag = _to_hashtag(np)
        if tag and tag not in seen and len(tag) > 3:
            seen.add(tag)
            hashtags.append(tag)

    return hashtags[:n]


def _extract_noun_phrases(text: str) -> List[str]:
    """
    Simple rule-based noun phrase extraction (no spaCy dependency).
    Looks for patterns like: 'Adj Noun', 'Noun Noun'.
    Returns a list of candidate phrases.
    """
    # Capitalised multi-word sequences often signal proper nouns / topics
    proper_nouns = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)

    # Common compound patterns (word + word)
    compound = re.findall(
        r"\b([a-z]+ (?:strategy|marketing|growth|content|media|business|"
        r"network|platform|community|brand|design|development|engineering|"
        r"analytics|automation|optimisation|optimization))\b",
        text,
        re.IGNORECASE,
    )

    return [p.strip() for p in proper_nouns + compound if len(p.strip()) > 3]
