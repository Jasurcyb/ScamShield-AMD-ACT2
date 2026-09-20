"""
tests/test_simulator.py — Pytest suite for Threat Simulation Lab.
Zero network dependencies. Verifies answer redaction, session store TTL,
double-answer prevention, difficulty validation, rate limiting, and template bank invariants.
"""

import time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.simulator import (
    TEMPLATE_BANK,
    ThreatSessionStore,
    rate_limiter,
    session_store,
)

client = TestClient(app)


def test_template_bank_invariants():
    """Verifies counts per difficulty, scam indicators >= 2, and legit indicators == []."""
    assert len(TEMPLATE_BANK) >= 18, f"Expected at least 18 templates, found {len(TEMPLATE_BANK)}"

    difficulties = {"easy": {"scam": 0, "legit": 0}, "medium": {"scam": 0, "legit": 0}, "hard": {"scam": 0, "legit": 0}}
    channels = set()

    for item in TEMPLATE_BANK:
        diff = item["difficulty"]
        channels.add(item["channel"])
        assert diff in difficulties, f"Unexpected difficulty: {diff}"

        if item["is_scam"]:
            difficulties[diff]["scam"] += 1
            assert len(item["indicators"]) >= 2, f"Scam item {item['id']} must have >= 2 indicators"
        else:
            difficulties[diff]["legit"] += 1
            assert item["indicators"] == [], f"Legit item {item['id']} must have empty indicators"

        assert len(item["tip"]) > 10, f"Item {item['id']} must have a descriptive tip"

    # Per difficulty: >= 3 scam and >= 2 legit
    for diff, counts in difficulties.items():
        assert counts["scam"] >= 3, f"Difficulty {diff} needs >= 3 scam templates, got {counts['scam']}"
        assert counts["legit"] >= 2, f"Difficulty {diff} needs >= 2 legit templates, got {counts['legit']}"

    assert {"email", "sms", "chat"}.issubset(channels)


@pytest.fixture
def test_client():
    import uuid
    # Use a unique IP per test to prevent rate limiter cross-contamination
    unique_ip = f"10.0.{uuid.uuid4().int % 200}.{uuid.uuid4().int % 200}"
    return TestClient(app, client=(unique_ip, 50000))


def test_threat_response_omits_answers_all_difficulties(test_client):
    """Asserts that raw JSON response never exposes is_scam or indicators across all difficulties."""
    for diff in ["easy", "medium", "hard"]:
        response = test_client.post("/api/simulate/threat", json={"difficulty": diff})
        assert response.status_code == 200
        data = response.json()

        assert "threat_id" in data
        assert data["difficulty"] == diff
        assert "channel" in data
        assert "sender" in data
        assert "subject" in data
        assert "body" in data

        # Security check: must NOT leak answer keys
        assert "is_scam" not in data, "Security leak: is_scam must not be returned!"
        assert "indicators" not in data, "Security leak: indicators must not be returned!"


def test_invalid_difficulty_returns_422(test_client):
    """Invalid difficulty string must be rejected with HTTP 422."""
    response = test_client.post("/api/simulate/threat", json={"difficulty": "impossible"})
    assert response.status_code == 422


def test_answer_correct_and_incorrect_paths(test_client):
    """Tests correct and incorrect guesses against the generated threat."""
    # Generate threat
    res = test_client.post("/api/simulate/threat", json={"difficulty": "medium"})
    assert res.status_code == 200
    threat_id = res.json()["threat_id"]

    # Inspect internal store to know true answer
    stored = session_store.get(threat_id)
    assert stored is not None
    true_is_scam = stored["is_scam"]

    # Submit correct answer
    ans_res = test_client.post("/api/simulate/answer", json={"threat_id": threat_id, "user_says_scam": true_is_scam})
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["correct"] is True
    assert ans_data["was_scam"] == true_is_scam
    assert "explanation" in ans_data
    assert "tip" in ans_data
    assert "score" in ans_data

    # Generate another threat to test incorrect answer
    res2 = test_client.post("/api/simulate/threat", json={"difficulty": "easy"})
    threat_id2 = res2.json()["threat_id"]
    stored2 = session_store.get(threat_id2)
    wrong_guess = not stored2["is_scam"]

    ans_res2 = test_client.post("/api/simulate/answer", json={"threat_id": threat_id2, "user_says_scam": wrong_guess})
    assert ans_res2.status_code == 200
    assert ans_res2.json()["correct"] is False


def test_double_answer_returns_409(test_client):
    """Answering the same threat twice must return HTTP 409 Conflict."""
    res = test_client.post("/api/simulate/threat", json={"difficulty": "easy"})
    threat_id = res.json()["threat_id"]

    # First answer
    res1 = test_client.post("/api/simulate/answer", json={"threat_id": threat_id, "user_says_scam": True})
    assert res1.status_code == 200

    # Second answer
    res2 = test_client.post("/api/simulate/answer", json={"threat_id": threat_id, "user_says_scam": True})
    assert res2.status_code == 409
    assert "already" in res2.json()["detail"].lower()


def test_unknown_or_expired_threat_returns_410(test_client):
    """Non-existent or expired threat ID returns HTTP 410."""
    res = test_client.post("/api/simulate/answer", json={"threat_id": "non_existent_id_12345", "user_says_scam": True})
    assert res.status_code == 410


def test_session_store_ttl_eviction(monkeypatch):
    """Monkeypatches time to verify session expires after 600s TTL."""
    current_time = 1000000.0

    def fake_time():
        return current_time

    store = ThreatSessionStore(ttl_seconds=600)
    monkeypatch.setattr(time, "time", fake_time)

    store.put("threat_1", {"is_scam": True, "indicators": ["test"]})
    assert store.get("threat_1") is not None

    # Advance time by 601 seconds
    current_time += 601.0
    assert store.get("threat_1") is None


def test_session_store_capacity_cap(monkeypatch):
    """Verifies oldest eviction when store exceeds max capacity."""
    current_time = 1000.0

    def fake_time():
        nonlocal current_time
        current_time += 1.0
        return current_time

    monkeypatch.setattr(time, "time", fake_time)
    small_store = ThreatSessionStore(ttl_seconds=600, max_entries=5)

    for i in range(7):
        small_store.put(f"threat_{i}", {"is_scam": True})

    # Earliest threats (0 and 1) should have been evicted
    assert small_store.get("threat_0") is None
    assert small_store.get("threat_1") is None
    assert small_store.get("threat_6") is not None


def test_rate_limiter_burst():
    """Verifies that exceeding 30 requests within window triggers HTTP 429."""
    burst_client = TestClient(app, client=("198.51.100.42", 50000))
    hit_429 = False

    for _ in range(35):
        res = burst_client.post("/api/simulate/threat", json={"difficulty": "easy"})
        if res.status_code == 429:
            hit_429 = True
            break

    assert hit_429, "Rate limiter did not trigger HTTP 429 upon burst requests!"


def test_route_aliases_work_identically():
    """Verifies both /simulate/threat and /api/simulate/threat work identically."""
    alias_client = TestClient(app, client=("10.10.10.10", 50000))
    res1 = alias_client.post("/simulate/threat", json={"difficulty": "easy"})
    assert res1.status_code == 200
    t_id = res1.json()["threat_id"]

    res2 = alias_client.post("/simulate/reveal", json={"threat_id": t_id, "user_says_scam": True})
    assert res2.status_code == 200

