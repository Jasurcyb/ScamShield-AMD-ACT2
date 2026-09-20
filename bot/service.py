"""Safe bridge between Telegram updates and ScamShield analysis."""

from __future__ import annotations

import html
import os
import tempfile
from pathlib import Path
from typing import Any

from aiogram import Bot

from app.router import HybridRouter
from app.security import FORENSIC_EXTENSIONS, MAX_TEXT_CHARS, MAX_UPLOAD_BYTES, validate_uploaded_file
from bot.localization import text


router_controller = HybridRouter()


def _risk_key(result: dict[str, Any]) -> str:
    risk = result.get("overall_risk", result.get("risk_level", "unknown"))
    return risk if risk in {"low", "medium", "high", "critical"} else "unknown"


def format_result(result: dict[str, Any], language: str) -> str:
    """Build a short, escaped HTML report suitable for Telegram."""
    risk = _risk_key(result)
    summary = result.get("final_summary") or result.get("summary") or text(language, "failed")
    recommendation = text(language, f"recommend_{risk}")
    report = text(
        language,
        "result",
        risk=text(language, risk),
        summary=html.escape(str(summary)),
        recommendation=html.escape(recommendation),
    )
    return f"{report}\n\n<i>{html.escape(text(language, 'disclaimer'))}</i>"


async def analyze_text_content(content: str) -> dict[str, Any]:
    if len(content) > MAX_TEXT_CHARS:
        raise ValueError("text_too_long")
    return await router_controller.route_decision(text=content)


async def analyze_telegram_file(
    bot: Bot,
    *,
    file_id: str,
    filename: str,
    caption: str | None = None,
) -> dict[str, Any]:
    """Download a Telegram file, validate it, analyse it, then erase it."""
    extension = Path(filename).suffix.lower()
    if extension not in FORENSIC_EXTENSIONS:
        raise ValueError("unsupported_format")

    descriptor, path = tempfile.mkstemp(suffix=extension)
    os.close(descriptor)
    try:
        telegram_file = await bot.get_file(file_id)
        await bot.download_file(telegram_file.file_path, destination=path)
        if os.path.getsize(path) > MAX_UPLOAD_BYTES:
            raise ValueError("file_too_large")
        validate_uploaded_file(path, extension)
        return await router_controller.route_decision(file_path=path, text=caption)
    finally:
        if os.path.exists(path):
            os.unlink(path)
