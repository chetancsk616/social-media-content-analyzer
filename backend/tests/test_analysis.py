"""
Integration tests for the /api/analyze/text endpoint.
These tests mock Gemini (via conftest.py) and test the full analysis pipeline.
"""

import pytest
from fastapi.testclient import TestClient


SAMPLE_POST = """
Did you know that 80% of social media posts fail to get meaningful engagement?
The secret isn't posting more — it's posting smarter.

Here's what top creators do differently:
1. They craft irresistible hooks in the first line.
2. They write for their audience, not for themselves.
3. They always end with a clear call-to-action.

Try this framework with your next post and watch your engagement skyrocket.
Comment below with your biggest challenge and I'll help you personally!

#SocialMedia #ContentStrategy #GrowthHacking
"""


def test_analyze_text_success(client: TestClient):
    response = client.post(
        "/api/analyze/text",
        json={"text": SAMPLE_POST},
    )
    assert response.status_code == 200
    data = response.json()

    # Top-level fields
    assert data["file_type"] == "text"
    assert data["extraction_method"] == "direct_text"
    assert len(data["extracted_text"]) > 0
    assert data["char_count"] > 0


def test_analyze_text_response_schema(client: TestClient):
    response = client.post("/api/analyze/text", json={"text": SAMPLE_POST})
    assert response.status_code == 200
    data = response.json()

    # Sentiment
    assert "sentiment" in data
    assert data["sentiment"]["label"] in ("POSITIVE", "NEGATIVE", "NEUTRAL")
    assert 0 <= data["sentiment"]["confidence"] <= 1

    # Metrics
    assert "metrics" in data
    assert data["metrics"]["word_count"] > 0
    assert data["metrics"]["sentence_count"] > 0
    assert data["metrics"]["readability_label"] in ("Easy", "Moderate", "Fairly Difficult", "Difficult")

    # Scores
    assert "scores" in data
    for key in ("hook", "cta", "clarity", "readability", "structure", "overall"):
        assert key in data["scores"]
        assert 0 <= data["scores"][key] <= 100

    # Keywords and hashtags
    assert isinstance(data["keywords"], list)
    assert isinstance(data["hashtags"], list)


def test_analyze_text_empty_fails(client: TestClient):
    response = client.post("/api/analyze/text", json={"text": "   "})
    assert response.status_code in (422, 400)


def test_analyze_text_short_text(client: TestClient):
    """Short text should still produce a valid response, not crash."""
    response = client.post(
        "/api/analyze/text",
        json={"text": "Buy now! Click the link."},
    )
    # Should succeed or give a validation error, not 500
    assert response.status_code in (200, 422)


def test_analyze_file_unsupported_type(client: TestClient):
    """Uploading an unsupported file type should return 422."""
    response = client.post(
        "/api/analyze",
        files={"file": ("test.txt", b"Hello world", "text/plain")},
    )
    assert response.status_code == 422


def test_analyze_file_empty(client: TestClient):
    """Uploading an empty file should return 422."""
    response = client.post(
        "/api/analyze",
        files={"file": ("test.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 422


def test_cta_detected_in_post(client: TestClient):
    post = "Check out the link in my bio and download your free guide today!"
    response = client.post("/api/analyze/text", json={"text": post})
    if response.status_code == 200:
        data = response.json()
        assert data["scores"]["cta"] > 0


def test_hook_score_for_question_hook(client: TestClient):
    post = "Did you know that 9 out of 10 startups fail in their first year? Here is why and how to avoid it."
    response = client.post("/api/analyze/text", json={"text": post})
    if response.status_code == 200:
        data = response.json()
        assert data["hook_analysis"]["score"] > 40
