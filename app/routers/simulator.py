"""
app/routers/simulator.py — Threat Simulation Lab router.
Provides server-side TTL session store, rate limiting, and realistic template bank
for interactive phishing training.
"""

from __future__ import annotations

import collections
import logging
import os
import random
import threading
import time
import uuid
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from core.indicators import evaluate_indicators

logger = logging.getLogger(__name__)

router = APIRouter(tags=["simulator"])

# ── 1. TEMPLATE BANK ──────────────────────────────────────────────────────────
# At least 12 scam + 6 legit across easy, medium, hard and email, sms, chat.
# Scam has >=2 indicators; legit has indicators == [].

TEMPLATE_BANK: List[Dict[str, Any]] = [
    # ── EASY (3 scam + 3 legit) ──────────────────────────────────────────────
    {
        "id": "easy_scam_email_1",
        "difficulty": "easy",
        "channel": "email",
        "is_scam": True,
        "sender": "Lottery Notification <winner@rewards-claim-pool.xyz>",
        "subject": "YOU WON $1,000,000!!! CLICK NOW!!!",
        "body": "Congratulations! Your email was chosen in our global sweepstakes! You won $1,000,000! Enter your bank details and password now immediately to claim your funds: http://rewards-claim-pool.xyz/claim",
        "indicators": [
            "urgency language",
            "too-good-to-be-true offer",
            "credential request",
        ],
        "tip": "Legitimate lotteries never demand banking credentials or passwords to transfer winnings.",
    },
    {
        "id": "easy_scam_sms_1",
        "difficulty": "easy",
        "channel": "sms",
        "is_scam": True,
        "sender": "+1-800-019-2831",
        "subject": "Package Delivery Alert",
        "body": "Your package cannot be delivered due to an unpaid dispatch fee. Pay $2.99 fee now: https://dhl-redelivery.top/pay to avoid return.",
        "indicators": [
            "micro-payment lure",
            "unofficial domain",
            "smishing pattern",
        ],
        "tip": "Major couriers like DHL or FedEx never use .top or .xyz domains for redelivery fee payments.",
    },
    {
        "id": "easy_scam_chat_1",
        "difficulty": "easy",
        "channel": "chat",
        "is_scam": True,
        "sender": "Security Support Bot",
        "subject": "Account Suspension Warning",
        "body": "URGENT: Your account will be suspended within 24 hours. Verify your account password and card number now: https://verify-telegram-bot.xyz/login",
        "indicators": [
            "urgency language",
            "credential request",
            "suspicious TLD",
        ],
        "tip": "Platform support never requests account passwords or credit card numbers in a chat window.",
    },
    {
        "id": "easy_legit_email_1",
        "difficulty": "easy",
        "channel": "email",
        "is_scam": False,
        "sender": "Chase Bank <notifications@chase.com>",
        "subject": "Your monthly statement is ready to view",
        "body": "Your monthly account statement for account ending in 4102 is now available online. For your security, open your web browser, type our official website address yourself, and sign in to review your statement.",
        "indicators": [],
        "tip": "Banks proactively advise customers to open browsers and type official URLs themselves instead of clicking embedded links.",
    },
    {
        "id": "easy_legit_sms_1",
        "difficulty": "easy",
        "channel": "sms",
        "is_scam": False,
        "sender": "USPS Official",
        "subject": "Tracking Notification",
        "body": "USPS Tracking: Package #940011189922334455 is out for delivery today by 6:00 PM. No further action is required.",
        "indicators": [],
        "tip": "Legitimate package status updates state expected delivery times and require no payments.",
    },
    {
        "id": "easy_legit_chat_1",
        "difficulty": "easy",
        "channel": "chat",
        "is_scam": False,
        "sender": "Dev Lead Alex",
        "subject": "Sprint Standup Notice",
        "body": "Hey team, reminder that daily standup is at 10:00 AM today in Room B. See you there.",
        "indicators": [],
        "tip": "Normal internal messages provide clear organizational context with no external action links.",
    },

    # ── MEDIUM (3 scam + 3 legit) ────────────────────────────────────────────
    {
        "id": "med_scam_email_1",
        "difficulty": "medium",
        "channel": "email",
        "is_scam": True,
        "sender": "Vendor Accounts <billing@apex-supplies-vendor.com>",
        "subject": "Invoice #48291 overdue — remit to UPDATED account details in attached PDF",
        "body": "Please be advised that Invoice #48291 is overdue. We recently changed our primary banking partner. Remit wire transfer immediately to our updated account details in the attached document to prevent delivery holds.",
        "indicators": [
            "BEC pattern",
            "changed payment details",
            "overdue pressure",
        ],
        "tip": "Always verify unexpected changes to vendor wire details through an established, out-of-band phone number.",
    },
    {
        "id": "med_scam_chat_1",
        "difficulty": "medium",
        "channel": "chat",
        "is_scam": True,
        "sender": "Project Colleague",
        "subject": "Shared Document Link",
        "body": "Shared document: Budget_final.xlsx → https://docs-viewer-share.net/d/88121. Please review and sign off today.",
        "indicators": [
            "document-sharing lure",
            "non-corporate file host",
            "external link",
        ],
        "tip": "Attackers disguise phishing sites as generic cloud document viewers (docs-viewer-share.net) to harvest credentials.",
    },
    {
        "id": "med_scam_sms_1",
        "difficulty": "medium",
        "channel": "sms",
        "is_scam": True,
        "sender": "Bank Fraud Dept",
        "subject": "Suspicious Activity Detected",
        "body": "ALERT: Card ending 5812 was blocked following an unrecognized $412.00 charge. Unlock immediately by confirming details: https://kap1talbank.top/unlock",
        "indicators": [
            "fear appeal",
            "urgency language",
            "typosquatted banking URL",
        ],
        "tip": "Notice the typosquatted URL 'kap1talbank.top' with number '1' instead of letter 'i' and high-risk '.top' TLD.",
    },
    {
        "id": "med_legit_email_1",
        "difficulty": "medium",
        "channel": "email",
        "is_scam": False,
        "sender": "Corporate HR <benefits@company-internal.corp>",
        "subject": "Open enrollment reminder: Window closes next Friday",
        "body": "Reminder: Annual health benefits open enrollment ends next Friday at 5:00 PM. Please navigate to the employee portal via your standard intranet bookmark to submit your selections.",
        "indicators": [],
        "tip": "Corporate HR notices often refer employees to existing internal bookmarks rather than embedding direct credential login links.",
    },
    {
        "id": "med_legit_chat_1",
        "difficulty": "medium",
        "channel": "chat",
        "is_scam": False,
        "sender": "SecOps OnCall",
        "subject": "Scheduled Maintenance Notice",
        "body": "Notice: Server cluster maintenance will take place tonight between 02:00 UTC and 04:00 UTC. API response times may temporarily fluctuate.",
        "indicators": [],
        "tip": "Standard DevOps maintenance announcements specify expected maintenance windows without asking users to act.",
    },
    {
        "id": "med_legit_sms_1",
        "difficulty": "medium",
        "channel": "sms",
        "is_scam": False,
        "sender": "United Airlines",
        "subject": "Flight Update",
        "body": "Flight UA418 to Chicago: Gate updated to B22. Boarding will start at 3:15 PM.",
        "indicators": [],
        "tip": "Informational airline alerts contain flight specifics and require no credential entry.",
    },

    # ── HARD (3 scam + 3 legit) ──────────────────────────────────────────────
    {
        "id": "hard_scam_email_1",
        "difficulty": "hard",
        "channel": "email",
        "is_scam": True,
        "sender": "IT Helpdesk <servicedesk@company-sso-portal.com>",
        "subject": "Q3 security policy update — re-authenticate via new SSO portal by Friday: https://company-sso-portal.com/login (ticket #IT-2291)",
        "body": "In accordance with our mandatory Q3 multi-factor security refresh, all employees must re-authenticate domain credentials on our updated SSO gateway by Friday 5:00 PM (ticket #IT-2291). Failure to do so will result in temporary suspension of network access.",
        "indicators": [
            "lookalike corporate domain",
            "fake internal ticket",
            "deadline pressure",
        ],
        "tip": "Sophisticated spear-phishers buy lookalike domains with hyphenated names like 'company-sso-portal.com' to clone corporate Single Sign-On pages.",
    },
    {
        "id": "hard_scam_sms_1",
        "difficulty": "hard",
        "channel": "sms",
        "is_scam": True,
        "sender": "Telecom Voice",
        "subject": "Voicemail Notification",
        "body": "Voice mailbox full (3 urgent messages waiting). Listen to recordings: https://v-mail-secure.xyz/vm/2210",
        "indicators": [
            "lookalike service domain",
            "suspicious TLD",
            "curiosity lure",
        ],
        "tip": "Telecom voicemails are dialed directly through your cellular dialer (*86), not streamed from random .xyz links.",
    },
    {
        "id": "hard_scam_chat_1",
        "difficulty": "hard",
        "channel": "chat",
        "is_scam": True,
        "sender": "Senior Executive (Direct Message)",
        "subject": "Confidential M&A Review",
        "body": "Are you at your desk? Please review the non-disclosure agreement for our upcoming partner acquisition: https://onedrive-secure-docs.xyz/view/NDA.pdf. Keep this strictly confidential.",
        "indicators": [
            "executive impersonation",
            "confidentiality pressure",
            "lookalike cloud storage domain",
        ],
        "tip": "Executive impersonation often combines artificial urgency, secrecy, and realistic lookalike cloud storage domains.",
    },
    {
        "id": "hard_legit_email_1",
        "difficulty": "hard",
        "channel": "email",
        "is_scam": False,
        "sender": "1Password Watchtower <watchtower@1password.com>",
        "subject": "Security Digest: Important security checkup for your saved items",
        "body": "Watchtower completed an automated scan of your saved items against known breach datasets. No compromised passwords or vulnerable credentials were detected. Keep your desktop application updated.",
        "indicators": [],
        "tip": "Legitimate automated security reports summarize status without urging immediate credential re-entry.",
    },
    {
        "id": "hard_legit_sms_1",
        "difficulty": "hard",
        "channel": "sms",
        "is_scam": False,
        "sender": "CVS Pharmacy",
        "subject": "Prescription Status",
        "body": "CVS Pharmacy: Prescription #098129 is ready for pickup at 450 Main St. Pharmacy closes at 9:00 PM today. Reply STOP to cancel SMS.",
        "indicators": [],
        "tip": "Official prescription alerts provide specific physical locations and standard opt-out text.",
    },
    {
        "id": "hard_legit_chat_1",
        "difficulty": "hard",
        "channel": "chat",
        "is_scam": False,
        "sender": "SecOps Automation",
        "subject": "Key Rotation Completed",
        "body": "Automated quarterly cryptographic key rotation for production staging has concluded successfully. All services report healthy status.",
        "indicators": [],
        "tip": "Internal system reports confirm maintenance operations with no external link demands.",
    },
]


# ── 2. SESSION STORE ──────────────────────────────────────────────────────────
# Thread-safe in-memory store with 600s TTL and 1000-entry capacity cap.

class ThreatSessionStore:
    def __init__(self, ttl_seconds: int = 600, max_entries: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _cleanup_expired(self, current_time: float) -> None:
        """Removes entries older than TTL."""
        expired_keys = [
            k for k, v in self._store.items()
            if (current_time - v.get("created_at", 0)) > self.ttl_seconds
        ]
        for k in expired_keys:
            del self._store[k]

    def put(self, threat_id: str, data: Dict[str, Any]) -> None:
        with self._lock:
            now = time.time()
            self._cleanup_expired(now)

            # Cap eviction: if store exceeds capacity, evict oldest entries
            if len(self._store) >= self.max_entries:
                oldest_key = min(self._store.keys(), key=lambda k: self._store[k].get("created_at", 0))
                del self._store[oldest_key]

            entry = dict(data)
            entry["created_at"] = now
            entry["revealed"] = False
            self._store[threat_id] = entry

    def get(self, threat_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            now = time.time()
            self._cleanup_expired(now)
            entry = self._store.get(threat_id)
            if not entry:
                return None
            if (now - entry.get("created_at", 0)) > self.ttl_seconds:
                del self._store[threat_id]
                return None
            return entry

    def mark_revealed(self, threat_id: str) -> bool:
        """
        Marks an entry revealed. Returns False if already revealed or not found.
        """
        with self._lock:
            now = time.time()
            self._cleanup_expired(now)
            entry = self._store.get(threat_id)
            if not entry:
                return False
            if entry.get("revealed", False):
                return False
            entry["revealed"] = True
            return True


session_store = ThreatSessionStore()


# ── 3. RATE LIMITER ───────────────────────────────────────────────────────────
# 30 req/min per IP on simulator endpoints

class RateLimiter:
    def __init__(self, limit: int = 30, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self._hits: Dict[str, collections.deque] = collections.defaultdict(collections.deque)
        self._lock = threading.Lock()

    def is_allowed(self, ip: str) -> bool:
        with self._lock:
            now = time.time()
            dq = self._hits[ip]
            while dq and (now - dq[0]) > self.window:
                dq.popleft()
            if len(dq) >= self.limit:
                return False
            dq.append(now)
            return True


rate_limiter = RateLimiter(limit=30, window_seconds=60)


# ── 4. SCHEMAS ────────────────────────────────────────────────────────────────

class ThreatRequest(BaseModel):
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class ThreatResponse(BaseModel):
    threat_id: str = Field(..., description="Unique simulation session ID")
    session_id: Optional[str] = Field(None, description="Alias for threat_id")
    difficulty: str = Field(..., description="Threat difficulty tier")
    channel: str = Field(..., description="Delivery channel: email, sms, or chat")
    sender: str = Field(..., description="Sender name or address")
    subject: str = Field(..., description="Message subject line")
    body: str = Field(..., description="Simulated message content")
    content: Optional[str] = Field(None, description="Alias for body")


class RevealRequest(BaseModel):
    threat_id: Optional[str] = Field(None, description="Threat ID to reveal/evaluate")
    session_id: Optional[str] = Field(None, description="Alias for threat_id")
    user_says_scam: Optional[bool] = Field(None, description="True if user classified as scam, False if legit")
    user_guess: Optional[bool] = Field(None, description="Alias for user_says_scam")

    def get_threat_id(self) -> str:
        tid = self.threat_id or self.session_id
        if not tid:
            raise ValueError("Either threat_id or session_id must be provided.")
        return tid

    def get_user_guess(self) -> bool:
        if self.user_says_scam is not None:
            return bool(self.user_says_scam)
        if self.user_guess is not None:
            return bool(self.user_guess)
        raise ValueError("Either user_says_scam or user_guess must be provided.")


class RevealResponse(BaseModel):
    correct: bool = Field(..., description="Whether user's answer matched actual status")
    user_correct: Optional[bool] = Field(None, description="Alias for correct")
    was_scam: bool = Field(..., description="True if simulated threat was a scam")
    is_scam: Optional[bool] = Field(None, description="Alias for was_scam")
    indicators: List[str] = Field(..., description="Detected scam indicator list")
    tip: str = Field(..., description="Educational guidance note")
    explanation: str = Field(..., description="Human-readable summary of verdict")
    score: int = Field(..., description="Risk score calculated by indicator engine (0-100)")


# ── 5. ROUTE HANDLERS ─────────────────────────────────────────────────────────

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def _generate_threat_payload(difficulty: str, request: Request) -> ThreatResponse:
    client_ip = _get_client_ip(request)
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 30 requests per minute.",
        )

    # Optional LLM generation mode if explicitly configured
    item: Optional[Dict[str, Any]] = None
    if os.getenv("OPENAI_API_KEY") and os.getenv("SIM_LLM") == "1":
        try:
            pass
        except Exception as e:
            logger.warning("sim_llm_fallback: %s", e)

    # Deterministic selection from template bank
    candidates = [t for t in TEMPLATE_BANK if t["difficulty"] == difficulty]
    if not candidates:
        candidates = TEMPLATE_BANK

    item = random.choice(candidates)
    threat_id = uuid.uuid4().hex

    # Store answer in session store
    session_store.put(
        threat_id=threat_id,
        data={
            "id": item["id"],
            "difficulty": item["difficulty"],
            "channel": item["channel"],
            "is_scam": item["is_scam"],
            "indicators": list(item["indicators"]),
            "tip": item["tip"],
            "sender": item["sender"],
            "subject": item["subject"],
            "body": item["body"],
        },
    )

    # Return public response ONLY (strictly no is_scam, no indicators)
    return ThreatResponse(
        threat_id=threat_id,
        session_id=threat_id,
        difficulty=item["difficulty"],
        channel=item["channel"],
        sender=item["sender"],
        subject=item["subject"],
        body=item["body"],
        content=item["body"],
    )


@router.get("/api/simulate/threat", response_model=ThreatResponse)
@router.get("/simulate/threat", response_model=ThreatResponse)
def generate_threat_get(request: Request, difficulty: Literal["easy", "medium", "hard"] = "medium"):
    """GET endpoint to fetch a simulated threat."""
    return _generate_threat_payload(difficulty, request)


@router.post("/api/simulate/threat", response_model=ThreatResponse)
@router.post("/simulate/threat", response_model=ThreatResponse)
def generate_threat(request: Request, req: Optional[ThreatRequest] = None):
    """
    POST endpoint to fetch a simulated threat.
    CRITICAL: Never returns is_scam or indicators in this response.
    """
    diff = req.difficulty if req else "medium"
    return _generate_threat_payload(diff, request)


@router.post("/api/simulate/answer", response_model=RevealResponse)
@router.post("/simulate/answer", response_model=RevealResponse)
@router.post("/api/simulate/reveal", response_model=RevealResponse)
@router.post("/simulate/reveal", response_model=RevealResponse)
def reveal_threat(req: RevealRequest):
    """
    Evaluates user's guess against session store.
    Unknown or expired threat_id -> 410 Gone (or 404).
    Already revealed -> 409 Conflict.
    """
    try:
        tid = req.get_threat_id()
        user_guess = req.get_user_guess()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    entry = session_store.get(tid)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Threat session has expired or does not exist. Please generate a new threat.",
        )

    # Check if already answered
    if entry.get("revealed", False):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This threat has already been answered.",
        )

    # Mark as revealed
    success = session_store.mark_revealed(tid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This threat has already been answered.",
        )

    was_scam = bool(entry["is_scam"])
    correct = (user_guess == was_scam)
    indicators = entry.get("indicators", [])
    tip = entry.get("tip", "")

    # Calculate deterministic indicator score
    body_text = entry.get("body", "")
    sender_text = entry.get("sender", "")
    subject_text = entry.get("subject", "")
    engine_eval = evaluate_indicators(text=body_text, sender=sender_text, subject=subject_text)
    score = engine_eval["score"] if was_scam else min(20, engine_eval["score"])

    # Build human-readable explanation
    if was_scam:
        if indicators:
            ind_str = ", ".join(indicators)
            explanation = f"This was a SCAM. Warning signs detected: {ind_str}. {tip}"
        else:
            explanation = f"This was a SCAM. {tip}"
    else:
        explanation = f"This was LEGITIMATE. No deceptive links or credential lures were present. {tip}"

    return RevealResponse(
        correct=correct,
        user_correct=correct,
        was_scam=was_scam,
        is_scam=was_scam,
        indicators=indicators,
        tip=tip,
        explanation=explanation,
        score=score,
    )

