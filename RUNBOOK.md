# ScamShield Runbook

## Overview
ScamShield is an open-source multimodal AI fraud and phishing detection system upgraded for the TLN Cybersecurity Challenge 2026.

## Technology Stack
- **Backend**: Python 3.12.13, FastAPI 0.139.2, Uvicorn 0.51.0, Starlette, Pydantic 2.12.5
- **Forensics & Inspection**: Pure-Python forensic scanners (`oletools`, `pypdf`, `Pillow`, `mutagen`, `Levenshtein`, `scipy`)
- **Telegram Bot**: Aiogram 3.30.0
- **Testing**: Pytest 9.1.1 (all tests run offline without network access)
- **Deployment**: Docker, Docker Compose, GHCR

---

## Local Development & Execution Commands

### 1. Prerequisites
- Python 3.11+ (Python 3.12 recommended)
- Git

### 2. Environment Setup (PowerShell / Windows)
```powershell
# Navigate to the project directory
cd scamshield_fastapi

# Create virtual environment if not already present
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (only existing pinned packages)
pip install -r requirements.txt
```

### 3. Run Automated Tests
All tests are 100% deterministic and execute completely offline with zero network calls:
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

### 4. Run Backend Server Locally
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation:
`http://localhost:8000/docs`

API Root Health Check:
`http://localhost:8000/`

---

## Existing API Endpoints
- `GET /`: Service banner and documentation link.
- `POST /analyze/vision`: Inspects uploaded images for font inconsistencies and tampering.
- `POST /analyze/stego`: Deep 9-probe forensic check (LSB, entropy, macros, trailing data).
- `POST /analyze/text`: Analyzes text for urgency hooks, typosquatting, and phishing.
- `POST /analyze/full`: Full multimodal analysis combining forensics and AI routing.

---

## Docker Execution
```bash
# Build and run FastAPI service
docker compose up --build
```
