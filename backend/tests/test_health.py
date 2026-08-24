"""Tests for the health endpoint."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "sentiment_model_loaded" in data
    assert "gemini_configured" in data


def test_health_schema(client: TestClient):
    response = client.get("/api/health")
    data = response.json()
    assert isinstance(data["sentiment_model_loaded"], bool)
    assert isinstance(data["gemini_configured"], bool)
