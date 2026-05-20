"""Smoke tests for the Finance Advisor Flask app.

These tests exercise the app without requiring any LLM API keys; the agent
falls back to the keyword router when ``LLM_PROVIDER=none``.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _force_no_llm(monkeypatch):
    """Force the keyword-router mode and scrub LLM keys for every test."""
    monkeypatch.setenv("LLM_PROVIDER", "none")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture()
def client():
    from app.api import create_app

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client


def test_app_starts() -> None:
    from app.api import create_app

    flask_app = create_app()
    assert flask_app is not None
    assert flask_app.name == "app.api"


def test_health_endpoint(client) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "finance-advisor"
    assert "timestamp" in payload
    # No sessions yet → llm_enabled is False under LLM_PROVIDER=none
    assert payload["llm_enabled"] is False


def test_chat_keyword_fallback(client) -> None:
    """Sample finance question should produce a non-empty response."""
    resp = client.post(
        "/api/chat",
        json={"session_id": "smoke", "message": "Explain compound interest"},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert "response" in payload
    assert isinstance(payload["response"], str)
    assert payload["response"].strip()
    assert payload["llm_enabled"] is False
    assert payload["mode"] == "none"


def test_chat_requires_message(client) -> None:
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400


def test_chat_advisory_disclaimer(client) -> None:
    """Investment questions must carry the NOT financial advice disclaimer."""
    resp = client.post(
        "/api/chat",
        json={
            "session_id": "smoke-invest",
            "message": "Should I invest in index funds?",
        },
    )
    assert resp.status_code == 200
    text = resp.get_json()["response"]
    assert "NOT financial advice" in text


def test_calculate_compound_endpoint(client) -> None:
    resp = client.post(
        "/api/calculate/compound",
        json={
            "principal": 10000,
            "annual_rate": 7,
            "years": 30,
            "compounds_per_year": 12,
        },
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    # 10000 * (1 + 0.07/12)^(360) ≈ 81,007
    assert payload["principal"] == 10000
    assert payload["years"] == 30
    assert payload["final_amount"] > 80000
    assert payload["final_amount"] < 82000
    assert payload["interest_earned"] == pytest.approx(
        payload["final_amount"] - 10000, rel=1e-6
    )


def test_calculate_emergency_endpoint(client) -> None:
    resp = client.post(
        "/api/calculate/emergency",
        json={"monthly_expenses": 3000, "months": 6},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["target_emergency_fund"] == 18000.0
    assert payload["months_of_coverage"] == 6


def test_list_concepts(client) -> None:
    resp = client.get("/api/concepts")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert isinstance(payload["concepts"], list)
    ids = {c["id"] for c in payload["concepts"]}
    assert "compound_interest" in ids
    assert "emergency_fund" in ids


def test_session_reset(client) -> None:
    resp = client.post("/api/session/reset", json={"session_id": "demo"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "reset"
