# Changelog

All notable changes to the ScamShield platform are documented in this file.

## [2.1.0] - 2026-09-20 (TLN Cybersecurity Challenge Edition)

### Added
- **Threat Simulation Lab (Backend & Frontend)**:
  - Added interactive simulation endpoints `POST /api/simulate/threat` and `POST /api/simulate/answer` with route aliases.
  - Implemented server-side thread-safe session store with 10-minute (600s) TTL, capacity cap of 1,000 entries, and oldest-eviction.
  - Added realistic 18-template bank spanning easy, medium, and hard difficulty tiers across email, SMS, and chat.
  - Added client-side privacy-first training statistics persisted in browser `localStorage` (`scamshield_lab_stats_v1`).
  - Added in-memory rate limiting (30 requests/minute per client IP) on simulation endpoints.
- **Deterministic Indicator Engine (`core/indicators.py`)**:
  - Pure Python deterministic indicator detection across 7 core rules (`URGENCY`, `CREDENTIAL_REQUEST`, `LOOKALIKE_DOMAIN`, `MICRO_PAYMENT_LURE`, `TOO_GOOD`, `PRESSURE_DEADLINE`, `SENDER_MISMATCH`).
  - Strict input sanitization with 10KB safe truncation and complete HTML escaping.
  - Predictable weighted scoring formula `min(100, 10 * sum(severities))` with guaranteed `score <= 20` for benign items.
- **Explainable AI (XAI) Contract & Component (`src/components/ExplainPanel.jsx`)**:
  - Extended multimodal analysis responses with standardized `explanation` object.
  - Interactive UI component featuring severity-colored indicator chips, pure-CSS per-modality confidence bars (Text, URL, Image), and risk-banded recommendation alerts.
  - Added `/analyze/explainable` and `/analyse/explainable` aliases.
- **Testing & Quality**:
  - Expanded test coverage from 22 to 63 offline tests covering indicator rules, boundaries, simulation flows, double-answer prevention, TTL eviction, and explainability schemas.
- **Documentation**:
  - Created `RUNBOOK.md` with local setup and test execution instructions.
  - Created `SUBMISSION.md` containing complete Devpost copy blocks and a 4-minute demo video script.
  - Updated `README.md` with AI tools disclosure, work split timeline, Threat Lab instructions, and security architecture.
