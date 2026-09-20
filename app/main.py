import os
import sys
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Ensure parent directory is on sys.path so 'tools', 'analyzer', 'database' can be imported
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from app.models import VisionResponse, StegoResponse, TextResponse, FullAnalysisResponse
from tools.vision_tool import vision_fraud_tool
from tools.stego_tool import stego_security_tool
from tools.text_url_tool import text_url_fraud_tool
from app.router import HybridRouter
from app.routers.simulator import router as simulator_router
from app.security import (
    FORENSIC_EXTENSIONS,
    IMAGE_FORMATS,
    MAX_TEXT_CHARS,
    RateLimitMiddleware,
    save_upload_limited,
)

app = FastAPI(
    title="ScamShield API",
    description="Multimodal Fraud Detection REST API for AMD Developer Hackathon: ACT II",
    version="2.0.0"
)

# Register Threat Simulation Lab router
app.include_router(simulator_router)

# Initialize the hybrid router
router_controller = HybridRouter()

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(RateLimitMiddleware)

# Telegram does not require CORS. Browser access is opt-in through an explicit
# allow-list, never a wildcard combined with credentials.
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if origin.strip()]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type", "Authorization"],
    )


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

from fastapi.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles

_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/")
def read_root(request: Request):
    accept = request.headers.get("accept", "")
    index_path = os.path.join(_STATIC_DIR, "index.html")
    if "text/html" in accept and os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Welcome to ScamShield API. Visit /docs for Swagger documentation."}


@app.get("/lab", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
def read_lab():
    index_path = os.path.join(_STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<h3>Threat Lab UI is building...</h3>")


# ── POST /analyze/vision ──────────────────────────────────────────────────────

@app.post("/analyze/vision", response_model=VisionResponse)
async def analyze_vision(file: UploadFile = File(...)):
    """
    Inspects an image (screenshot, receipt, etc.) for visual signs of forgery or manipulation.
    """
    temp_path = None
    try:
        temp_path, _ = await save_upload_limited(file, allowed_extensions=IMAGE_FORMATS)
        result = await vision_fraud_tool(temp_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Анализ изображения временно недоступен. Повторите попытку позже.") from e

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# ── POST /analyze/stego ───────────────────────────────────────────────────────

@app.post("/analyze/stego", response_model=StegoResponse)
async def analyze_stego(file: UploadFile = File(...)):
    """
    Performs multi-layered forensic steganography and threat keyword checks on the uploaded file.
    """
    temp_path = None
    try:
        temp_path, _ = await save_upload_limited(file, allowed_extensions=FORENSIC_EXTENSIONS)
        result = await stego_security_tool(temp_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Анализ файла временно недоступен. Повторите попытку позже.") from e

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# ── POST /analyze/text ────────────────────────────────────────────────────────

@app.post("/analyze/text", response_model=TextResponse)
async def analyze_text(text: str = Form("")):
    """
    Inspects text messages and URLs for phishing, urgency triggers, and typo-squatted domains.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Текст превышает допустимый объём.")

    try:
        result = await text_url_fraud_tool(text)
        from core.indicators import build_explanation, evaluate_indicators
        eval_res = evaluate_indicators(text=text)
        result["explanation"] = build_explanation(score=eval_res["score"], text=text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Анализ текста временно недоступен. Повторите попытку позже.") from e


# ── POST /analyze/full (Hybrid Routed Analysis) ───────────────────────────────

@app.post("/analyze/full", response_model=FullAnalysisResponse)
@app.post("/analyze/explainable", response_model=FullAnalysisResponse)
@app.post("/analyse/explainable", response_model=FullAnalysisResponse)
async def analyze_full(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Hybrid routed endpoint that performs full multimodal analysis.
    Intelligently routes LLM tasks locally (Ollama) or remotely (Fireworks/Claude/Gemini)
    to minimize token costs while maintaining high forensic accuracy.
    """
    if not file and not text:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least one input for analysis: a file (upload) or a text message (form-data)."
        )
    if text and len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Текст превышает допустимый объём.")

    temp_path = None
    try:
        if file:
            temp_path, _ = await save_upload_limited(file, allowed_extensions=FORENSIC_EXTENSIONS)

        # Run router controller decision
        result = await router_controller.route_decision(file_path=temp_path, text=text)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Анализ временно недоступен. Повторите попытку позже.") from e

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
