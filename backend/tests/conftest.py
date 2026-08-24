"""
Pytest configuration and shared fixtures.

Mock the Gemini service so tests never require a real API key.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.analysis import GeminiRecommendations


@pytest.fixture(scope="session")
def mock_gemini():
    """
    Patch the Gemini generate_recommendations function.

    We patch it in the module where it is *called* (the orchestrator),
    which is the correct mock target.
    """
    mock_result = GeminiRecommendations(
        available=True,
        recommendations=["Add a stronger CTA", "Use more numbers"],
        strengths=["Good sentiment"],
        weaknesses=["Weak hook"],
        improved_post="Improved version of the post.",
        alternative_hooks=["Did you know…"],
    )
    # Patch in both the source module and where it is imported/used
    with patch(
        "app.services.gemini_service.generate_recommendations",
        return_value=mock_result,
    ):
        yield mock_result


@pytest.fixture(scope="session")
def client(mock_gemini):
    """Test client with mocked Gemini."""
    with TestClient(app) as c:
        yield c
