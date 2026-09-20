"""
tests/test_explanation.py — Unit tests for Explainable AI contract and response models.
Verifies risk bands (39->low, 40->medium, 69->medium, 70->high), recommendations,
modality confidence bounds in [0.0, 1.0], null modality serialization, and empty fallback.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from core.indicators import build_explanation


@pytest.fixture
def client():
    import uuid
    unique_ip = f"10.2.{uuid.uuid4().int % 200}.{uuid.uuid4().int % 200}"
    return TestClient(app, client=(unique_ip, 50000))


def test_band_boundary_39_low():
    res = build_explanation(score=39, text="Meeting reminder for tomorrow morning at 9am.")
    assert res["risk_band"] == "low"
    assert "Low risk" in res["recommendation"]
    assert "standard caution" in res["recommendation"]


def test_band_boundary_40_medium():
    res = build_explanation(score=40, text="Please review this file.")
    assert res["risk_band"] == "medium"
    assert "Verify the sender independently" in res["recommendation"]


def test_band_boundary_69_medium():
    res = build_explanation(score=69, text="Urgent wire request from vendor.")
    assert res["risk_band"] == "medium"
    assert "Verify the sender independently" in res["recommendation"]


def test_band_boundary_70_high():
    res = build_explanation(score=70, text="Invoice overdue! Wire funds now immediately.")
    assert res["risk_band"] == "high"
    assert "Do not interact" in res["recommendation"]
    assert "Report and delete" in res["recommendation"]


def test_empty_indicators_fallback_for_clean_low_risk():
    res = build_explanation(score=10, text="Thank you, see you tomorrow.")
    assert res["risk_band"] == "low"
    assert len(res["indicators"]) > 0
    labels = [ind.get("label") if isinstance(ind, dict) else str(ind) for ind in res["indicators"]]
    assert any("No strong malicious signals detected" in label for label in labels)


def test_modality_confidences_within_zero_to_one():
    res = build_explanation(
        score=85,
        text="URGENT: Click http://paypa1.top to enter your password immediately!",
        has_image=True,
        image_indicators=[{"label": "Tampered font layout", "severity": 3}]
    )
    conf = res["confidence_by_modality"]
    for modality, val in conf.items():
        if val is not None:
            assert 0.0 <= val <= 1.0, f"Modality {modality} confidence {val} not in [0.0, 1.0]"


def test_null_modality_serialization_when_modality_absent():
    # Text-only input without URLs or images
    res = build_explanation(score=15, text="Hello world with no links.", has_image=False)
    conf = res["confidence_by_modality"]
    assert conf["text"] is not None
    assert conf["url"] is None, "URL confidence must be null when no URL is analyzed"
    assert conf["image"] is None, "Image confidence must be null when no image is uploaded"


def test_llm_confidence_blending():
    # Verify the 0.7 * det + 0.3 * llm blending documented in requirement
    res_no_llm = build_explanation(score=60, text="URGENT: Enter your password now!", llm_confidence=None)
    res_with_llm = build_explanation(score=60, text="URGENT: Enter your password now!", llm_confidence=0.9)
    assert res_with_llm["confidence_by_modality"]["text"] != res_no_llm["confidence_by_modality"]["text"]


def test_analyze_full_response_includes_explanation(client):
    """Verifies that POST /analyze/full returns an explanation block matching contract."""
    response = client.post(
        "/analyze/full",
        data={"text": "URGENT: Verify your account password at http://paypa1-security.xyz immediately"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    exp = data["explanation"]
    assert "indicators" in exp
    assert "score_breakdown" in exp
    assert "confidence_by_modality" in exp
    assert "risk_band" in exp
    assert "recommendation" in exp
    assert exp["risk_band"] in ["low", "medium", "high"]


def test_explainable_route_aliases(client):
    """Verifies that /analyze/explainable and /analyse/explainable aliases respond with explanation."""
    for path in ["/analyze/explainable", "/analyse/explainable"]:
        res = client.post(path, data={"text": "Meeting notes with no links."})
        assert res.status_code == 200
        data = res.json()
        assert "explanation" in data
        assert data["explanation"]["risk_band"] == "low"
