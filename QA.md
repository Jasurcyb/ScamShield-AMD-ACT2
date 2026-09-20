# ScamShield Manual QA Checklist & Verification Matrix

## Overview
This document outlines manual verification steps for testing ScamShield in production or staging environments during the TLN Cybersecurity Challenge 2026.

---

## 1. Full User Click-Through Verification

### Test 1.1: Threat Simulation Lab — Easy Tier
- [x] Navigate to `http://localhost:8000/lab` or click `🎯 Training Lab`.
- [x] Select the `Easy` segmented difficulty button.
- [x] Click `⚡ Generate threat`.
- [x] Verify message card renders with channel badge (e.g. `📧 EMAIL`), sender, subject, and body.
- [x] Confirm no indicator spoiler or answer leaks are visible in the UI or DevTools network inspector.
- [x] Click `🚨 This is a SCAM`.
- [x] Verify result banner appears with green styling ("🎉 Correct! It was a SCAM"), risk score (e.g. 80/100), detected indicators, explanation, and pro-tip.
- [x] Verify stats bar increments total count and current streak.
- [x] Click `Next threat →` and verify next challenge loads seamlessly.

### Test 1.2: Threat Simulation Lab — Medium & Hard Tiers
- [x] Select `Medium` → generate threat (e.g. BEC invoice update) → verify answer flow.
- [x] Select `Hard` → generate threat (e.g. lookalike corporate SSO portal) → verify answer flow.
- [x] Verify streaks increment on correct answers and reset to 0 upon incorrect answer.
- [x] Test `Reset stats` button: prompt confirmation appears; clicking OK resets stats to 0% (0/0) with streaks cleared.
- [x] Refresh the browser page (`F5`) and confirm stats remain persisted from `localStorage`.

### Test 1.3: Live Multimodal Scanner & Explainable AI Panel
- [x] Switch to `🔍 Live Scanner` tab.
- [x] Enter text: `URGENT: Your account has been suspended! Verify your password at http://paypa1-security.xyz immediately.`
- [x] Click `🚀 Analyze Threat`.
- [x] Verify verdict renders `Overall Risk: HIGH` and probability.
- [x] Scroll to the **Explainable AI Panel** (`🔍 Why this score?`):
  - [x] Risk band badge displays `HIGH`.
  - [x] Red recommendation banner renders: `"Do not interact with this content. Report and delete."`
  - [x] Severity chips render with icons (🔗 for lookalike domain, 📝 for urgency).
  - [x] Pure-CSS confidence bars animate: Text (~67%), URL (~67%), Image (`N/A`).

---

## 2. Keyboard-Only Navigation & Accessibility (a11y)
- [x] Open web app and press `Tab` key repeatedly.
- [x] Verify focus moves logically: Brand → Nav Tabs (`🎯 Training Lab`, `🔍 Live Scanner`) → Stats Reset → Difficulty Buttons → Generate Button → Answer Buttons.
- [x] Verify focused elements have clear, high-contrast visual focus rings.
- [x] Verify `Enter` and `Space` activate segmented radio controls and action buttons.
- [x] Verify screen readers announce recommendations via `role="status"` and `aria-live="polite"`.

---

## 3. Mobile Responsiveness & 390px Viewport Check
- [x] Open DevTools device toolbar and set screen width to `390px` (iPhone 12/13/14 viewport).
- [x] Verify layout adjusts gracefully without horizontal scroll:
  - [x] Header wraps title and navigation buttons cleanly.
  - [x] Stats bar wraps metrics into stacked rows.
  - [x] Controls bar stacks difficulty segmented control and `Generate threat` button full-width.
  - [x] Answer buttons (`🚨 This is a SCAM` and `✅ This is LEGIT`) stack vertically at 100% width.
  - [x] Mail body text wraps long URLs and text strings cleanly.

---

## 4. Edge Cases & Boundary Conditions
- [x] **Double-Click Debounce**: Rapidly double-clicking `⚡ Generate threat` triggers only a single request (500ms debounce guard).
- [x] **Corrupted localStorage**: Manually setting `localStorage.setItem('scamshield_lab_stats_v1', 'invalid_json{')` and reloading page triggers safe fallback to `{correct: 0, total: 0, streak: 0, best: 0}` without crashing.
- [x] **Expired Threat Submission**: Calling answer endpoint with an expired or non-existent ID returns HTTP 410 with user-friendly alert: *"Session expired, generate a new threat"*.
- [x] **Rate Limit Burst**: Firing >30 requests/minute from a single IP triggers HTTP 429 with toast message: *"Too many requests, wait a minute"*.
- [x] **Empty Input Scanner**: Submitting empty text and file in Live Scanner triggers form validation alert without server request.
