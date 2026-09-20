# ScamShield Deployment Notes

## Production Deployment Guide for TLN Cybersecurity Challenge 2026

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12 (tested on Python 3.12.13)
- **Node.js**: 18.x, 20.x, or 22.x (zero external npm dependencies required; uses standard built-in node script `build.js`)
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, Alpine 3.19+), macOS 12+, or Windows 10/11 / Windows Server
- **Memory & Storage**: 1 GB RAM minimum (2 GB recommended for vision models), 500 MB disk space.

---

### 2. Environment Variables Table

| Name | Required | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `PORT` | Optional | `8000` | Port for the Uvicorn ASGI web server |
| `MAX_REQUESTS_PER_MINUTE` | Optional | `30` | Per-client IP rate limiting threshold |
| `CORS_ALLOW_ORIGINS` | Optional | `*` | Comma-separated list of allowed CORS origins |
| `SIM_LLM` | Optional | `0` | Set to `1` to enable optional LLM-generated simulation threats |
| `OPENAI_API_KEY` | Optional | None | OpenAI API key for optional dynamic LLM threat generation |
| `ANTHROPIC_API_KEY` | Optional | None | Claude API key for multimodal vision inspection |
| `FIREWORKS_API_KEY` | Optional | None | Fireworks AI API key for fast serverless LLM inference |
| `GEMINI_API_KEY` | Optional | None | Google Gemini API key for multimodal analysis |
| `OLLAMA_BASE_URL` | Optional | `http://localhost:11434` | Endpoint for local vision/text inference |
| `TELEGRAM_BOT_TOKEN` | Optional | None | Bot token if running the Telegram bot service |

---

### 3. Step-by-Step Deploy Instructions

#### Option A: VPS with Docker & Docker Compose (Recommended)
1. **Clone repository**:
   ```bash
   git clone <repository_url>
   cd scamshield_fastapi
   ```
2. **Build frontend assets**:
   ```bash
   npm run build
   ```
3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if setting optional keys or custom port
   ```
4. **Launch containerized stack**:
   ```bash
   docker compose up -d --build
   ```
5. **Verify running containers**:
   ```bash
   docker compose ps
   curl -I http://localhost:8000/
   ```

#### Option B: Cloud Hosting (Render / Railway / Fly.io)
1. **Repository root**: Set root directory to `scamshield_fastapi` (or deploy from repository root).
2. **Build Command**:
   ```bash
   pip install -r requirements.txt && npm run build
   ```
3. **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
4. **Environment Variables**: Add `PORT` (assigned automatically by cloud provider).
5. **Static Mount**: FastAPI automatically serves the built React UI from `/app/static` at `/`, `/lab`, and `/app`.

#### Option C: Native Bare Metal / Local Server
```bash
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
npm run build
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 4. Health Check & Service Endpoints

- **Health Check URL**: `GET /` (Returns HTTP 200 with JSON message for API clients, or serves interactive web UI for browser requests)
- **OpenAPI / Swagger Documentation**: `GET /docs` (Returns HTTP 200)
- **OpenAPI Schema**: `GET /openapi.json` (Returns HTTP 200)
- **Threat Simulation Lab UI**: `GET /lab` or `GET /app` (Returns HTTP 200 with HTML)
- **Threat Generator Endpoint**: `GET /simulate/threat` or `POST /simulate/threat` (Returns HTTP 200)
- **Threat Reveal Endpoint**: `POST /simulate/reveal` (Returns HTTP 200)
- **Full Multimodal Analysis**: `POST /analyze/full` (Returns HTTP 200 with Explainable AI contract)

---

### 5. Known Limitations & Tradeoffs Made

1. **In-Memory TTL Session Store for Simulator**:
   - *Design Decision*: Uses a thread-safe Python dictionary with 600-second TTL and a 1,000-entry max capacity cap (oldest eviction).
   - *Tradeoff*: For multi-instance load-balanced deployments behind a round-robin proxy, sessions are instance-local unless sticky sessions are configured, or backed by Redis. For single-container or worker clusters, this eliminates external dependencies and provides sub-millisecond lookups.

2. **Supply Chain Security & Zero-Dependency Frontend**:
   - *Design Decision*: In light of the August 2026 Shai-Hulud supply-chain attacks targeting npm caching libraries (`keyv`, `cacheable`, `flat-cache`), no third-party npm packages were installed. A native Node.js build script (`build.js`) validates all React components and packages them directly.
   - *Tradeoff*: Bundles React 18 and Babel via verified CDN / standalone bundles rather than complex Webpack/Vite dependency trees, guaranteeing immunity against compromised node packages.

3. **Pure Python Deterministic Fallback**:
   - *Design Decision*: Every single endpoint operates 100% offline without requiring any external LLM or cloud API keys. The deterministic indicator engine executes regex heuristics and weighted scoring in < 2ms.
   - *Tradeoff*: High throughput, predictable risk scoring, and zero operational cloud cost, while still offering plug-and-play enrichment when `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` are provided.
