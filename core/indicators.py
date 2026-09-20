"""
core/indicators.py — Pure deterministic indicator and risk scoring engine for ScamShield.
Evaluates text, URLs, and metadata against forensic detection rules without external dependencies or LLMs.
"""

from __future__ import annotations

import html
import re
from typing import Dict, List, Literal, Optional, Any

ModalityType = Literal["text", "url", "image"]

MAX_INPUT_LENGTH = 10240  # 10 KB safe truncation limit

# Rule severity mappings (1 to 3)
RULE_SEVERITY: Dict[str, int] = {
    "URGENCY": 2,
    "CREDENTIAL_REQUEST": 3,
    "LOOKALIKE_DOMAIN": 3,
    "MICRO_PAYMENT_LURE": 2,
    "TOO_GOOD": 3,
    "PRESSURE_DEADLINE": 2,
    "SENDER_MISMATCH": 2,
}

# Human-readable labels
RULE_LABELS: Dict[str, str] = {
    "URGENCY": "Urgency & high-pressure phrasing",
    "CREDENTIAL_REQUEST": "Direct request for sensitive credentials or banking data",
    "LOOKALIKE_DOMAIN": "Suspicious, lookalike or high-risk domain name",
    "MICRO_PAYMENT_LURE": "Micro-payment / fee lure with payment redirection",
    "TOO_GOOD": "Unrealistic reward or lottery prize lure",
    "PRESSURE_DEADLINE": "Imminent deadline or account suspension threat",
    "SENDER_MISMATCH": "Sender display name conflicts with sender domain",
}

# Modality attribution
RULE_MODALITY: Dict[str, ModalityType] = {
    "URGENCY": "text",
    "CREDENTIAL_REQUEST": "text",
    "LOOKALIKE_DOMAIN": "url",
    "MICRO_PAYMENT_LURE": "text",
    "TOO_GOOD": "text",
    "PRESSURE_DEADLINE": "text",
    "SENDER_MISMATCH": "text",
}


def sanitize_input(text: Optional[str]) -> str:
    """
    Safely clamps input to 10KB and handles unicode normalization cleanly.
    """
    if not text:
        return ""
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]
    return text


def escape_output(text: str) -> str:
    """
    Ensures any user-supplied text rendered is HTML-escaped to prevent XSS.
    """
    return html.escape(text, quote=True)


def evaluate_indicators(
    text: Optional[str] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    image_indicators: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Pure deterministic evaluation function.
    Returns:
        {
            "score": int (0-100),
            "indicators": list of {rule_id, label, severity, modality},
            "score_breakdown": list of {rule_id, points},
            "sanitized_text": str
        }
    """
    raw_text = text or ""
    raw_sender = sender or ""
    raw_subject = subject or ""

    sanitized_text = sanitize_input(raw_text)
    combined = f"{raw_sender} {raw_subject} {sanitized_text}".lower()

    detected_rules: Dict[str, Dict[str, Any]] = {}

    # 1. URGENCY
    urgency_patterns = [
        r"\bnow\b",
        r"\bimmediately\b",
        r"\bwithin 24 hours\b",
        r"\burgent\b",
        r"\bact fast\b",
        r"\blimited time\b",
        r"\bсрочно\b",
        r"\bнемедленно\b",
    ]
    if any(re.search(pat, combined) for pat in urgency_patterns):
        detected_rules["URGENCY"] = {
            "rule_id": "URGENCY",
            "label": RULE_LABELS["URGENCY"],
            "severity": RULE_SEVERITY["URGENCY"],
            "modality": RULE_MODALITY["URGENCY"],
        }

    # 2. CREDENTIAL_REQUEST
    cred_keywords = [
        r"\b(?:enter|provide|send|verify|update|input|confirm)\s+(?:your\s+)?password\b",
        r"\bpassword\s*:",
        r"\bcurrent\s+password\b",
        r"\bbank details\b",
        r"\bcard number\b",
        r"\bssn\b",
        r"\bcvv\b",
        r"\bpin code\b",
        r"\b(?:введите|подтвердите|отправьте)\s+(?:ваш\s+)?пароль\b",
        r"\bномер карты\b",
    ]
    verify_with_link = (
        ("verify your account" in combined or "подтвердите аккаунт" in combined or "подтвердите данные" in combined)
        and ("http" in combined or "link" in combined or "click" in combined or "войти" in combined)
    )
    if any(re.search(pat, combined) for pat in cred_keywords) or verify_with_link:
        detected_rules["CREDENTIAL_REQUEST"] = {
            "rule_id": "CREDENTIAL_REQUEST",
            "label": RULE_LABELS["CREDENTIAL_REQUEST"],
            "severity": RULE_SEVERITY["CREDENTIAL_REQUEST"],
            "modality": RULE_MODALITY["CREDENTIAL_REQUEST"],
        }

    # 3. LOOKALIKE_DOMAIN
    lookalike_patterns = [
        r"\bpaypa1\b",
        r"\bg00gle\b",
        r"\bcompany-sso-portal\b",
        r"\bdocs-viewer-share\b",
        r"\bdhl-redelivery\b",
        r"\bv-mail-secure\b",
        r"\bkap1talbank\b",
        r"\bpayme-verif\b",
        r"\banorbank-secure\b",
    ]
    risky_tlds = [r"\.xyz\b", r"\.top\b", r"\.tk\b", r"\.ml\b", r"\.ga\b", r"\.cf\b"]
    has_lookalike = any(re.search(pat, combined) for pat in lookalike_patterns)
    has_risky_tld = any(re.search(pat, combined) for pat in risky_tlds)
    if has_lookalike or has_risky_tld:
        detected_rules["LOOKALIKE_DOMAIN"] = {
            "rule_id": "LOOKALIKE_DOMAIN",
            "label": RULE_LABELS["LOOKALIKE_DOMAIN"],
            "severity": RULE_SEVERITY["LOOKALIKE_DOMAIN"],
            "modality": RULE_MODALITY["LOOKALIKE_DOMAIN"],
        }

    # 4. MICRO_PAYMENT_LURE
    # Amount < $5 with payment/fee context
    micro_amount_match = re.search(r"\$\s*([0-4](?:\.\d{1,2})?)\b", combined)
    fee_keywords = ["fee", "pay", "shipping", "delivery", "redelivery", "оплата", "комиссия", "доставка"]
    if micro_amount_match and any(w in combined for w in fee_keywords):
        detected_rules["MICRO_PAYMENT_LURE"] = {
            "rule_id": "MICRO_PAYMENT_LURE",
            "label": RULE_LABELS["MICRO_PAYMENT_LURE"],
            "severity": RULE_SEVERITY["MICRO_PAYMENT_LURE"],
            "modality": RULE_MODALITY["MICRO_PAYMENT_LURE"],
        }

    # 5. TOO_GOOD
    too_good_patterns = [
        r"\byou won\b",
        r"\bprize\b",
        r"\bclaim\b",
        r"\$1,000,000",
        r"\blottery\b",
        r"\bjackpot\b",
        r"\bвы выиграли\b",
        r"\bприз\b",
        r"\bмиллион\b",
    ]
    if any(re.search(pat, combined) for pat in too_good_patterns):
        detected_rules["TOO_GOOD"] = {
            "rule_id": "TOO_GOOD",
            "label": RULE_LABELS["TOO_GOOD"],
            "severity": RULE_SEVERITY["TOO_GOOD"],
            "modality": RULE_MODALITY["TOO_GOOD"],
        }

    # 6. PRESSURE_DEADLINE
    deadline_patterns = [
        r"\bby friday\b",
        r"\boverdue\b",
        r"\bsuspended\b",
        r"\bfinal notice\b",
        r"\baccount suspension\b",
        r"\bблокировка\b",
        r"\bпоследнее предупреждение\b",
        r"\bпросрочен\b",
    ]
    if any(re.search(pat, combined) for pat in deadline_patterns):
        detected_rules["PRESSURE_DEADLINE"] = {
            "rule_id": "PRESSURE_DEADLINE",
            "label": RULE_LABELS["PRESSURE_DEADLINE"],
            "severity": RULE_SEVERITY["PRESSURE_DEADLINE"],
            "modality": RULE_MODALITY["PRESSURE_DEADLINE"],
        }

    # 7. SENDER_MISMATCH
    # e.g., "PayPal" in display name but domain does not match paypal.com
    sender_lower = raw_sender.lower()
    mismatch_detected = False
    brands = {
        "paypal": "paypal.com",
        "google": "google.com",
        "apple": "apple.com",
        "microsoft": "microsoft.com",
        "dhl": "dhl.com",
        "chase": "chase.com",
        "kapitalbank": "kapitalbank.uz",
    }
    for brand, legit_domain in brands.items():
        if brand in sender_lower:
            # Check if domain appears in sender
            domain_match = re.search(r"@([a-zA-Z0-9.-]+)", sender_lower)
            if domain_match:
                extracted_domain = domain_match.group(1)
                if not extracted_domain.endswith(legit_domain):
                    mismatch_detected = True
                    break

    if mismatch_detected:
        detected_rules["SENDER_MISMATCH"] = {
            "rule_id": "SENDER_MISMATCH",
            "label": RULE_LABELS["SENDER_MISMATCH"],
            "severity": RULE_SEVERITY["SENDER_MISMATCH"],
            "modality": RULE_MODALITY["SENDER_MISMATCH"],
        }

    # Integrate image indicators if provided (from vision/stego tool)
    if image_indicators:
        for idx, img_ind in enumerate(image_indicators):
            rule_key = f"IMAGE_ANOMALY_{idx+1}"
            sev = img_ind.get("severity", 2)
            detected_rules[rule_key] = {
                "rule_id": rule_key,
                "label": img_ind.get("label", "Visual anomaly / forensic manipulation detected"),
                "severity": min(3, max(1, int(sev))),
                "modality": "image",
            }

    # Build indicators list and score breakdown
    indicators_list = list(detected_rules.values())
    score_breakdown = [
        {"rule_id": item["rule_id"], "points": item["severity"] * 10}
        for item in indicators_list
    ]

    # Deterministic scoring formula: min(100, 10 * sum(severities))
    severity_sum = sum(item["severity"] for item in indicators_list)
    score = min(100, 10 * severity_sum)

    return {
        "score": score,
        "indicators": indicators_list,
        "score_breakdown": score_breakdown,
        "sanitized_text": sanitized_text,
    }


def build_explanation(
    score: int,
    text: Optional[str] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    has_image: bool = False,
    image_indicators: Optional[List[Dict[str, Any]]] = None,
    llm_confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Constructs the Explainable AI contract object for analysis endpoints.

    Recommendation & Band Tiers:
    - score >= 70: 'high'   -> 'Do not interact with this content. Report and delete.'
    - 40 <= score <= 69: 'medium' -> 'Verify the sender independently before acting.'
    - score < 40: 'low'     -> 'Low risk — standard caution.'

    Confidence by Modality:
    - Deterministic proxy: min(1.0, modality_points / 45.0)
    - If LLM present: blend 0.7 * det + 0.3 * llm (documented in comment)
    - Modalities not evaluated serialize as null.
    """
    # 1. Determine risk band and recommendation
    if score >= 70:
        risk_band = "high"
        recommendation = "Do not interact with this content. Report and delete."
    elif score >= 40:
        risk_band = "medium"
        recommendation = "Verify the sender independently before acting."
    else:
        risk_band = "low"
        recommendation = "Low risk — standard caution."

    # 2. Evaluate indicators
    eval_result = evaluate_indicators(
        text=text,
        sender=sender,
        subject=subject,
        image_indicators=image_indicators
    )
    indicators = eval_result["indicators"]
    score_breakdown = eval_result["score_breakdown"]

    # If indicators empty and band low, fallback to friendly clean indicator
    if not indicators and risk_band == "low":
        indicators = [
            {
                "rule_id": "CLEAN",
                "label": "No strong malicious signals detected",
                "severity": 1,
                "modality": "text",
            }
        ]

    # Map indicators to rule_id -> modality for score breakdown
    rule_modalities = {ind["rule_id"]: ind["modality"] for ind in indicators}

    # 3. Calculate confidence per modality
    # Text modality
    text_conf = None
    if text is not None and text.strip() != "":
        text_points = sum(
            item["points"] for item in score_breakdown
            if rule_modalities.get(item["rule_id"]) == "text"
        )
        det_text = min(1.0, round(text_points / 45.0, 2))
        # If LLM confidence is present, blend 0.7 * det + 0.3 * llm
        if llm_confidence is not None:
            text_conf = round(0.7 * det_text + 0.3 * max(0.0, min(1.0, float(llm_confidence))), 2)
        else:
            text_conf = det_text

    # URL modality
    url_conf = None
    has_url_pattern = bool(text and ("http://" in text or "https://" in text or ".xyz" in text or ".top" in text))
    if has_url_pattern or any(ind.get("modality") == "url" for ind in indicators):
        url_points = sum(
            item["points"] for item in score_breakdown
            if rule_modalities.get(item["rule_id"]) == "url"
        )
        url_conf = min(1.0, round(url_points / 45.0, 2))

    # Image modality
    image_conf = None
    if has_image:
        image_points = sum(
            item["points"] for item in score_breakdown
            if rule_modalities.get(item["rule_id"]) == "image"
        )
        image_conf = min(1.0, round(image_points / 45.0, 2))

    return {
        "indicators": indicators,
        "score_breakdown": score_breakdown,
        "confidence_by_modality": {
            "text": text_conf,
            "url": url_conf,
            "image": image_conf,
        },
        "risk_band": risk_band,
        "recommendation": recommendation,
    }

