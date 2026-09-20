import asyncio

from app.router import HybridRouter


def test_router_uses_selected_provider_for_agent_calls(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("FIREWORKS_API_KEY", "test-key")
    selected_providers = []

    async def text_stub(_text, provider=None):
        selected_providers.append(provider)
        return {"risk_level": "high", "text_findings": ["Фишинг"], "summary": "Опасный текст."}

    async def summary_stub(_reports, _provider):
        return "Опасный текст."

    monkeypatch.setattr("app.router.text_url_fraud_tool", text_stub)
    router = HybridRouter()
    monkeypatch.setattr(router, "_generate_final_summary", summary_stub)

    result = asyncio.run(router.route_decision(text="Urgent: verify your bank card at http://example.com"))

    assert selected_providers == ["fireworks"]
    assert result["router_metadata"]["selected_provider"] == "fireworks"
    assert result["router_metadata"]["tokens_used"] is None


def test_router_prefers_local_for_short_benign_text(monkeypatch):
    monkeypatch.setenv("FIREWORKS_API_KEY", "test-key")
    router = HybridRouter()

    assert router._determine_llm_provider(text_len=20, has_phishing_hints=False) == "local"
