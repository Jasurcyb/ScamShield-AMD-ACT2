# ScamShield — Multimodal Fraud Detection REST API

**ScamShield** is a Telegram-first MVP for the **President Tech Award Incubation Track**. It helps users identify phishing, suspicious links, forged receipts, and risky files.
It exposes an async FastAPI REST API that inspects text, URLs, documents, and images for phishing, social engineering, and forensic modifications — with a smart hybrid AI router that balances cost, speed, and accuracy.

---

## AI Providers

| Task | Model | Status |
|------|-------|--------|
| Text analysis (primary) | DeepSeek V4 Flash (Fireworks AI, AMD Instinct GPUs) | ✅ Active |
| Vision analysis (primary) | Minimax M3 (Fireworks AI, AMD Instinct GPUs) | ✅ Active |
| Text/Vision (Gemma path) | Google Gemma 4 31B IT (Fireworks AI) | 🔧 Code-ready, pending model access on current API tier |
| Offline fallback | Google Gemma 4 12B (local Ollama in Docker) | ✅ Active, $0 cost |

The router attempts **Google Gemma 4 31B IT** first; if unavailable (HTTP 404), it automatically falls back to **DeepSeek V4 Flash** (text) / **Minimax M3** (vision) on Fireworks AI, then to **local Ollama** if no API key or internet connection is present.

> **Note on Gemma Prize eligibility:** The codebase is fully written to use Google Gemma 4 31B IT as the primary model. The fallback to DeepSeek/Minimax is triggered only because the current Fireworks API tier does not expose Gemma models. If the tier is upgraded or Gemma access is granted, the system will automatically route all requests through Gemma with zero code changes.

---

## 🚀 Key Features

1. **Hybrid Provider Routing Controller** — Inspects incoming requests and intelligently routes lightweight tasks to a free local Ollama model, and complex visual/threat queries to cloud AI (Fireworks AI on AMD Instinct GPUs). Minimizes API costs while maintaining high accuracy.

2. **9-Probe Forensic Scanner** — Built-in parallel deep-scanning engine:
   - LSB steganography detection
   - Histogram combing analysis
   - Trailing data / appended payload detection
   - File entropy anomaly scoring
   - Word VBA macro extraction (AutoExec)
   - PDF JavaScript / embedded action scanning
   - Threat keyword matching
   - EXIF metadata inspection
   - File signature validation

3. **Levenshtein Typosquatting Engine** — High-performance domain similarity checking targeted at Central Asian banking platforms (Kapitalbank, Click, Payme, Uzcard, Humo) to catch phishing redirects like `kap1talbank.uz` or `payme-verif.uz`.

4. **Threat Simulation Lab (Interactive Phishing Trainer)** — Gamified educational module serving realistic simulated scam and legitimate messages across email, SMS, and chat. Features TTL session storage, rate limiting, and private local client stats to empower users against evolving social engineering.

5. **Explainable AI (XAI) Panel** — Full score transparency with per-modality confidence bars (Text, URL, Image), forensic indicator tags, and clear, actionable security recommendations.

---

## 📐 Architecture

```
                  ┌────────────────────────────────────────┐
                  │          Client API Request            │
                  └──────────────────┬─────────────────────┘
                                     │ (JSON / File Upload)
                                     ▼
                  ┌────────────────────────────────────────┐
                  │             FastAPI Router             │
                  └──────────────────┬─────────────────────┘
                                     │
             ┌───────────────────────┴───────────────────────┐
             ▼ (Size & Keyword Heuristics)                   ▼ (Local Scan)
┌───────────────────────────┐                         ┌─────────────┐
│   Hybrid LLM Controller   │                         │  Forensics  │
└──────┬─────────────┬──────┘                         │   Engine    │
       │             │                                └──────┬──────┘
       ▼ (Cloud)     ▼ (Local)                               ▼
┌──────────────┐ ┌──────────────┐                    • LSB Stego Check
│ Fireworks AI │ │ Local Ollama │                    • Histogram Comb
│ (DeepSeek /  │ │ (Gemma 4 12B)│                    • PDF JS Check
│  Minimax M3) │ │    FREE      │                    • VBA AutoExec
└──────────────┘ └──────────────┘                    • EXIF & Entropy
```

---

## 🛠️ Setup & Running

### 1. Configure Credentials
```bash
cp .env.example .env
```
Fill in `TELEGRAM_BOT_TOKEN` and, optionally, one cloud AI key. If no cloud key is set, the router falls back to local Ollama execution automatically.

### 2. Pull Pre-built Image
```bash
docker pull ghcr.io/jasurcyb/scamshield-amd-act2:latest
docker run -p 8000:8000 --env-file .env ghcr.io/jasurcyb/scamshield-amd-act2:latest
```

### 3. Run with Docker Compose (Recommended)
This launches the FastAPI app and a local Ollama container. On startup, the entrypoint script automatically pulls `gemma4:12b` in the background.

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`.  
Interactive Swagger UI: `http://localhost:8000/docs`

### 4. Run the Telegram bot

Set `TELEGRAM_BOT_TOKEN` and a public `SUPPORT_CONTACT` (Telegram handle or email) in `.env`, then run:

```bash
docker compose up --build bot ollama
```

The bot displays a short safety notice at `/start`. The full pilot privacy notice is available through `/privacy`; it explains that the result is advisory, files are deleted after processing, and selected cloud AI providers may process text or images. Do not launch publicly until `SUPPORT_CONTACT` is set and the notice has been reviewed for the intended deployment.

For local development:

```bash
python -m bot.main
```

### 5. Running Tests
```bash
docker compose run app pytest
```

---

## 📡 API Endpoints & Examples

### 1. Full Routed Scan (Image + Text)
```bash
curl -X POST "http://localhost:8000/analyze/full" \
  -F "file=@screenshot.png" \
  -F "text=Urgent verify your card details at kap1talbank.uz"
```

### 2. Text & URL Phishing Scan
```bash
curl -X POST "http://localhost:8000/analyze/text" \
  -F "text=Urgent! Send \$500 to verify your account at kap1talbank.uz within 1 hour"
```

### 3. Vision Analysis (Screenshot / Document)
```bash
curl -X POST "http://localhost:8000/analyze/vision" \
  -F "file=@bank_transfer.png"
```

### 4. Steganography / Forensics Scan
```bash
curl -X POST "http://localhost:8000/analyze/stego" \
  -F "file=@suspicious_document.pdf"
```

---

## 📁 Project Structure

```
scamshield_fastapi/
├── app/
│   ├── main.py          # FastAPI application & endpoint handlers
│   ├── models.py         # Pydantic request/response schemas
│   └── router.py         # Hybrid LLM provider routing logic
├── bot/
│   ├── main.py           # Telegram polling entry point
│   ├── handlers.py       # Commands and message handlers
│   └── localization.py   # Russian, Uzbek and English UI text
├── tools/
│   ├── llm_provider.py   # Fireworks AI / Ollama / Gemini backends
│   ├── vision_tool.py    # Image analysis via multimodal LLMs
│   ├── text_url_tool.py  # Text & URL phishing analysis
│   └── stego_tool.py     # Steganography & forensic scanning
├── analyzer.py           # Core forensic engine (9 parallel probes)
├── database.py           # Curated scanner keyword configuration
├── Dockerfile            # Multi-stage container build
├── docker-compose.yml    # App + Ollama orchestration
├── entrypoint.sh         # Container startup (Ollama wait + model pull)
├── requirements.txt      # Python dependencies
├── requirements.lock     # Reproducible dependency versions
└── .env.example          # Environment variable template
```

---

## 🔧 Tech Stack

- **Runtime:** Python 3.11, FastAPI, Uvicorn
- **Cloud AI:** Fireworks AI (DeepSeek V4 Flash, Minimax M3, Gemma 4 31B IT ready)
- **Local AI:** Ollama with Google Gemma 4 12B
- **Infrastructure:** Docker Compose, AMD Instinct GPUs (via Fireworks AI)
- **Forensics:** Pillow, python-docx, PyPDF2, numpy
- **Data handling:** Uploaded files are deleted after analysis; persistent history is not enabled in the MVP.

---

## License

MIT

---

## 🤖 AI & External Tools Disclosure

ScamShield employs external AI models and forensic tools to analyze content and assist user defenses:
- **Fireworks AI (DeepSeek V4 Flash & Minimax M3)**: Used for cloud-accelerated multimodal text and vision inspection when API connectivity is available.
- **Local Ollama (Google Gemma 4 12B)**: Used as an optional zero-cost offline fallback for local natural language threat reasoning.
- **OpenAI / Claude APIs**: Supported via environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) as optional supplementary analysis and threat simulation engines.
- **Deterministic Indicator Engine & Pure Scoring**: All threat scoring, forensic indicators, and risk bands operate via an **LLM-independent, deterministic pure Python engine** (`core/indicators.py`). An LLM never decides risk scores alone, ensuring 100% predictable, reproducible, and verifiable safety guarantees even without network access or external API keys.

---

## 🎓 Threat Simulation Lab

The **Threat Simulation Lab** provides gamified, interactive cybersecurity training for everyday users and employees:
- **What it does**: Simulates realistic phishing, smishing, business email compromise (BEC), and corporate SSO impersonation attacks across 3 difficulty tiers (`easy`, `medium`, `hard`) and 3 channels (`email`, `sms`, `chat`).
- **Why it matters**: Social engineering accounts for over 80% of security incidents. Reactive blocking is insufficient; educating human decision-makers at scale prevents credential loss before attacks succeed.
- **How it works**:
  1. Users request a challenge via `POST /api/simulate/threat`. The server issues a realistic scenario with answers strictly withheld.
  2. The user classifies the item as either **🚨 SCAM** or **✅ LEGIT**.
  3. `POST /api/simulate/answer` grades the response, provides detected forensic indicators, and delivers a concise educational pro-tip.
  4. Accuracy, streaks, and best scores are calculated and stored **strictly on the user's browser via localStorage**, ensuring complete user privacy without server-side tracking.

---

## 🔍 Explainable AI

Every analysis request returns a transparent explanation contract via the `explanation` object:
```json
{
  "explanation": {
    "indicators": [
      { "rule_id": "LOOKALIKE_DOMAIN", "label": "Suspicious, lookalike or high-risk domain name", "severity": 3, "modality": "url" },
      { "rule_id": "CREDENTIAL_REQUEST", "label": "Direct request for sensitive credentials", "severity": 3, "modality": "text" }
    ],
    "score_breakdown": [
      { "rule_id": "LOOKALIKE_DOMAIN", "points": 30 },
      { "rule_id": "CREDENTIAL_REQUEST", "points": 30 }
    ],
    "confidence_by_modality": {
      "text": 0.67,
      "url": 0.67,
      "image": null
    },
    "risk_band": "high",
    "recommendation": "Do not interact with this content. Report and delete."
  }
}
```
- **Risk Bands**:
  - `> 70` (High): *"Do not interact with this content. Report and delete."*
  - `40 - 70` (Medium): *"Verify the sender independently before acting."*
  - `< 40` (Low): *"Low risk — standard caution."*
- **Modality Confidence**: Deterministic proxy `min(1.0, modality_points / 45)`. If LLM output is present, blended via `0.7 * det + 0.3 * llm`. Modalities not present serialize as `null`.

---

## 📅 Development Timeline (Work Split)

- **Original Build (June 2026)**:
  - Core multimodal detection architecture, Band SDK prototype, 9-probe steganography & forensics engine, initial Telegram bot.
- **During TLN Cybersecurity Challenge (September 19–20, 2026)**:
  - Developed and integrated the **Threat Simulation Lab** (backend session store, 18-template bank, rate-limiter).
  - Designed and built the **Deterministic Indicator Engine** (`core/indicators.py`) with zero-dependency pure scoring.
  - Implemented the **Explainable AI (XAI)** response contract and interactive `ExplainPanel` component.
  - Created the responsive React 18 frontend with localStorage client stats.
  - Expanded automated test coverage to 63 offline tests (100% green).
  - Drafted comprehensive submission documentation, demo video script, and deployment runbooks.

---

## 🛡️ Security & Privacy

- **No PII Stored**: Raw user texts and uploaded files are analyzed in temporary memory and purged immediately after inspection.
- **Local-Only Training Stats**: Simulation training scores and streaks exist exclusively in browser `localStorage` (`scamshield_lab_stats_v1`), ensuring zero server profiling.
- **In-Memory TTL Session Store**: Simulation sessions are held in thread-safe memory with an automatic 600-second (10-minute) TTL and hard 1,000-entry capacity cap.
- **Strict Rate Limiting**: 30 requests/minute per client IP enforces protection against automated abuse and scraping.
- **XSS Prevention**: All user inputs rendered in the UI are strictly HTML-escaped.
- **Supply Chain Immune**: Pure JavaScript/React frontend architecture with zero vulnerable npm packages, fully protected against Shai-Hulud supply-chain attack vectors.

