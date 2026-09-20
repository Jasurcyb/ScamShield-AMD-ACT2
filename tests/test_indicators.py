"""
tests/test_indicators.py — Offline unit tests for deterministic indicator & scoring engine.
Covers positive and negative detections for all 7 rules, boundary conditions,
unicode safety, HTML escaping, and 10KB truncation.
"""

import pytest
from core.indicators import evaluate_indicators, sanitize_input, escape_output, MAX_INPUT_LENGTH


def test_urgency_rule_positive():
    res = evaluate_indicators(text="Please respond immediately! This is an urgent notice.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "URGENCY" in rule_ids
    assert res["score"] >= 20


def test_urgency_rule_negative():
    res = evaluate_indicators(text="Here is the report from yesterday's weekly sync.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "URGENCY" not in rule_ids


def test_credential_request_positive():
    res = evaluate_indicators(text="Please verify your account at https://secure-login.com and enter your password.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "CREDENTIAL_REQUEST" in rule_ids
    assert any(ind["severity"] == 3 for ind in res["indicators"] if ind["rule_id"] == "CREDENTIAL_REQUEST")


def test_credential_request_negative():
    res = evaluate_indicators(text="Please find the monthly budget breakdown attached.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "CREDENTIAL_REQUEST" not in rule_ids


def test_lookalike_domain_positive():
    res = evaluate_indicators(text="Log in via https://paypa1-security.xyz to update your profile.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "LOOKALIKE_DOMAIN" in rule_ids
    assert any(ind["modality"] == "url" for ind in res["indicators"] if ind["rule_id"] == "LOOKALIKE_DOMAIN")


def test_lookalike_domain_negative():
    res = evaluate_indicators(text="Visit the official site at https://paypal.com/help")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "LOOKALIKE_DOMAIN" not in rule_ids


def test_micro_payment_lure_positive():
    res = evaluate_indicators(text="Package redelivery fee of $2.99 required. Pay now: http://deliver.net")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "MICRO_PAYMENT_LURE" in rule_ids


def test_micro_payment_lure_negative():
    res = evaluate_indicators(text="The total invoice for Q3 software licensing is $5000.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "MICRO_PAYMENT_LURE" not in rule_ids


def test_too_good_positive():
    res = evaluate_indicators(text="Congratulations! You won $1,000,000 in our international lottery! Claim prize.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "TOO_GOOD" in rule_ids


def test_too_good_negative():
    res = evaluate_indicators(text="We received your scholarship application for review.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "TOO_GOOD" not in rule_ids


def test_pressure_deadline_positive():
    res = evaluate_indicators(text="Invoice #48291 is overdue. Immediate suspension unless settled by Friday.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "PRESSURE_DEADLINE" in rule_ids


def test_pressure_deadline_negative():
    res = evaluate_indicators(text="The project roadmap meeting is scheduled for next Tuesday at 10 AM.")
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "PRESSURE_DEADLINE" not in rule_ids


def test_sender_mismatch_positive():
    res = evaluate_indicators(
        text="Please confirm your transaction.",
        sender="PayPal Security <alert@fake-service.xyz>"
    )
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "SENDER_MISMATCH" in rule_ids


def test_sender_mismatch_negative():
    res = evaluate_indicators(
        text="Your receipt is available.",
        sender="PayPal Support <service@paypal.com>"
    )
    rule_ids = [ind["rule_id"] for ind in res["indicators"]]
    assert "SENDER_MISMATCH" not in rule_ids


def test_score_formula_and_cap():
    # Trigger almost all rules to verify cap at 100
    compound_scam = (
        "URGENT: You won $1,000,000 prize! Pay $2.99 redelivery fee now immediately. "
        "Account suspended by Friday unless you verify your account password at http://paypa1-login.top"
    )
    res = evaluate_indicators(text=compound_scam, sender="PayPal Team <scam@bad-host.xyz>")
    assert res["score"] == 100
    assert len(res["score_breakdown"]) >= 5


def test_legit_templates_score_lte_20():
    legit_cases = [
        ("Your monthly statement is ready. Please log in to your banking portal by typing the address yourself.", "Bank Notification <notice@chase.com>"),
        ("Internal meeting notes: Reviewed Q3 sprint items, no action items pending.", "Alice <alice@internal-company.com>"),
        ("Your order #884920 has shipped via official carrier. Tracking available in your portal account.", "Shipping <orders@official-store.com>"),
        ("Password manager security digest: No compromised passwords found in your vault. Keep using the desktop app.", "Security Digest <digest@1password.com>"),
    ]
    for text, sender in legit_cases:
        res = evaluate_indicators(text=text, sender=sender)
        assert res["score"] <= 20, f"Legit message scored too high ({res['score']}): {text}"


def test_unicode_and_emoji_handling():
    unicode_text = "🚨 Внимание! Срочно подтвердите пароль карты или блокировка счета! 💳🔒"
    res = evaluate_indicators(text=unicode_text)
    assert res["score"] > 0
    assert any(ind["rule_id"] in ["URGENCY", "CREDENTIAL_REQUEST", "PRESSURE_DEADLINE"] for ind in res["indicators"])


def test_input_truncation_at_10kb():
    massive_text = "normal text " * 2000  # > 20KB
    assert len(massive_text) > MAX_INPUT_LENGTH
    sanitized = sanitize_input(massive_text)
    assert len(sanitized) == MAX_INPUT_LENGTH
    res = evaluate_indicators(text=massive_text)
    assert len(res["sanitized_text"]) == MAX_INPUT_LENGTH


def test_html_escaping():
    malicious_html = "<script>alert('xss')</script><b>Click</b> \"here\" & 'win'"
    escaped = escape_output(malicious_html)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
    assert "&quot;here&quot;" in escaped
    assert "&#x27;win&#x27;" in escaped or "&#39;win&#39;" in escaped or "&apos;win&apos;" in escaped


def test_empty_input_scores_zero():
    res = evaluate_indicators(text="", sender="", subject="")
    assert res["score"] == 0
    assert res["indicators"] == []
    assert res["score_breakdown"] == []


def test_image_indicators_integration():
    img_ind = [{"rule_id": "STAMP_CLONING", "label": "Cloned pixel region detected", "severity": 3}]
    res = evaluate_indicators(text="Hello world", image_indicators=img_ind)
    assert res["score"] == 30
    assert any(ind["modality"] == "image" for ind in res["indicators"])
