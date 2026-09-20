# TLN Cybersecurity Challenge 2026 — Project Submission Pack

## Devpost Submission Fields (Copy-Paste Ready)

### Project Name
**ScamShield — Multimodal AI Fraud Detection & Training Platform**

### Tagline
Empowering citizens and enterprises against evolving cyber-fraud with multimodal forensic scanning, transparent explainable AI, and gamified threat simulation training.

---

### Description

#### Problem
Digital fraud and social engineering have exploded worldwide, with cyber-scams inflicting over $1 trillion in annual consumer and enterprise losses. In emerging markets and Central Asia, fraudsters leverage localized linguistic manipulation, lookalike corporate and banking SSO domains (e.g. typosquatted domestic payment services), smishing fee traps, and forged document receipts. Traditional signature-based defenses fail against novel, generative phishing, while users lack practical tools to build threat detection reflexes.

#### Solution
**ScamShield** is an open-source, multimodal AI security platform combining **proactive prevention** and **preventative education**:
1. **Multimodal Forensic AI Scanner**: Inspects unstructured texts, URLs, receipts, and documents across 9 parallel forensic probes (LSB steganography, histogram analysis, macro scripts, metadata anomalies) and hybrid AI models.
2. **Transparent Explainable AI (XAI)**: Demystifies detection with per-modality confidence bars (Text, URL, Image), categorized forensic indicator chips, and clear, risk-banded security recommendations.
3. **Threat Simulation Lab**: A gamified training environment that challenges users to classify realistic spear-phishing, smishing, and BEC invoice scams across difficulty tiers, tracking performance strictly on-device to protect privacy.

#### Key Features
- **Deterministic Pure Scoring Engine**: Core indicator rules and scoring operate via pure Python without LLM dependencies, guaranteeing predictable, verifiable results offline.
- **Explainable AI (XAI) Panel**: Visual breakdown of forensic indicators, confidence percentages per modality, and risk-tier action advice.
- **Gamified Training Lab**: Server-side 10-minute TTL session store, rate limiting (30 req/min per IP), and 18 diverse scenarios across email, SMS, and chat.
- **Privacy-First Client Stats**: Accuracy and streaks persist exclusively in client browser `localStorage` without tracking or server telemetry.
- **Resilient Hybrid Fallback**: Operates 100% offline with zero external API keys, while scaling to cloud AI when keys are provided.

#### Target Users
- **Everyday Consumers & Families**: Verifying suspicious messages, links, and fake payment receipts.
- **SMEs & Corporate Employees**: Continuous, accessible phishing resilience training to halt BEC invoice and SSO credential thefts.
- **Financial Institutions & FinTech Platforms**: API-first integration for incoming payment screenshot and transaction validation.

---

### Technologies Used
Python 3.12, FastAPI, Uvicorn, Starlette, Pydantic, Pytest, React 18, Pillow, python-docx, pypdf, mutagen, oletools, Levenshtein, Docker, Docker Compose, Fireworks AI

---

### Project Links
- **Demo Link (Live URL):** [LIVE_URL]
- **GitHub Repository:** [GITHUB_URL]
- **Demo Video (YouTube):** [VIDEO_URL]

---

## 4-Minute Demo Video Script

| Timestamp | Screen / Visual | Voiceover Script |
| :--- | :--- | :--- |
| **0:00 - 0:40** | **Slide / Title Screen + Shocking Stats**<br>Display global fraud statistics ($1T+ loss) and realistic examples: smishing delivery text and lookalike banking login. | *"Welcome to ScamShield. In 2026, social engineering accounts for over 80% of cybersecurity breaches. Scammers now use generative AI to clone corporate portals, craft realistic invoice updates, and trick millions of users. Antivirus software alone is not enough — we need automated detection paired with human cyber-resilience. That's why we built ScamShield."* |
| **0:40 - 2:00** | **Live Analysis Demo showing ExplainPanel**<br>Open web app tab `🔍 Live Scanner`. Paste a spear-phishing email with lookalike domain `https://company-sso-portal.com/login` and fake IT ticket. Click *Analyze Threat*. | *"Let's test our live scanner on an urgent IT update. In under 200 milliseconds, ScamShield's engine evaluates the text and URL. Notice the Explainable AI panel: instead of a black-box score, it explains WHY. We see high risk (80%), detected indicators for Lookalike Corporate Domain and Urgency Language, and confidence broken down per modality — 67% on text, 67% on URL, and null for unanalyzed images. The recommendation is crystal clear: Do not interact. Report and delete."* |
| **2:00 - 3:10** | **Threat Simulation Lab Walkthrough**<br>Switch to `🎯 Training Lab`.<br>1. Select *Easy* → Generate Threat (Lottery lure) → click *This is a SCAM* → Green success banner + indicators.<br>2. Select *Medium* → Generate Threat (BEC invoice update) → answer → show pro-tip.<br>3. Select *Hard* → Generate Threat (Telecom voicemail link) → answer → highlight streak and accuracy counter. | *"Prevention starts with education. In the Threat Simulation Lab, users test their reflexes across realistic attacks and legitimate communications. Let's try Easy: an urgent lottery email. We click 'This is a SCAM' — correct! We see the breakdown and pro-tip. Now Medium: a tricky vendor invoice with changed wire details. Next, Hard: a voicemail SMS redirecting to a .xyz site. Notice our stats bar: accuracy updates live and streaks are tracked. Best of all, training stats live strictly in the user's browser localStorage — zero tracking, zero telemetry."* |
| **3:10 - 3:40** | **Architecture & Security Deep-Dive**<br>Display architecture diagram and security principles: TTL store, rate limiting, deterministic scoring. | *"Under the hood, ScamShield is built on FastAPI and React 18. Our indicator engine is a pure deterministic Python module that runs 100% offline with zero external dependencies. Training sessions utilize a thread-safe 10-minute TTL store with oldest-eviction caps and per-IP rate limits to prevent abuse. All outputs are strictly HTML-escaped, and the frontend is immune to modern npm supply chain attacks."* |
| **3:40 - 4:00** | **Impact & Future Vision**<br>Display roadmap, Adaption Platform mention, and GitHub link. | *"ScamShield bridges the gap between AI automation and human vigilance. Looking ahead, we plan to leverage Adaption Platform credits to synthesize massive, multilingual training datasets covering Central Asian and global dialects. Try the live demo at the link below. Thank you!"* |
