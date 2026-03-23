import httpx

from app.ai.prompts import build_prompt
from app.core.config import get_settings
from app.models.schemas import (
    AIDifferentialRequest,
    AILiteratureRequest,
    AIQueryRequest,
    AIResponse,
    AITranslateRequest,
)

DISCLAIMER_FR = "Ceci est généré par l'IA et doit être vérifié par un clinicien."
DISCLAIMER_EN = "This is AI-generated and must be verified by a clinician."


async def _call_inference(payload: dict) -> dict:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{settings.ai_inference_url}/generate", json=payload)
        resp.raise_for_status()
        return resp.json()


def _build_response(raw: dict, locale: str) -> AIResponse:
    confidence = raw.get("confidence", 0.0)
    disclaimer = DISCLAIMER_FR if locale == "fr" else DISCLAIMER_EN
    if confidence < 0.6:
        disclaimer = f"⚠️ Faible confiance ({confidence:.0%}). " + disclaimer
    return AIResponse(
        answer=raw.get("answer", ""),
        confidence=confidence,
        sources=raw.get("sources", []),
        disclaimer=disclaimer,
        locale=locale,
    )


async def query(data: AIQueryRequest) -> AIResponse:
    locale = data.context.get("locale", "fr")
    p = build_prompt("query", locale=locale, question=data.question)
    raw = await _call_inference({**p, "max_tokens": data.max_tokens})
    return _build_response(raw, locale)


async def differential(data: AIDifferentialRequest) -> AIResponse:
    p = build_prompt(
        "differential", symptoms=", ".join(data.symptoms),
        vitals=data.vitals, demographics=data.demographics, history=data.history,
    )
    raw = await _call_inference({**p, "max_tokens": 2048})
    return _build_response(raw, data.locale)


async def literature(data: AILiteratureRequest) -> AIResponse:
    p = build_prompt("literature", topic=data.topic)
    raw = await _call_inference({**p, "max_tokens": 2048})
    return _build_response(raw, data.locale)


async def translate(data: AITranslateRequest) -> AIResponse:
    target_language = "French" if data.target_locale == "fr" else "English"
    p = build_prompt("translate", target_language=target_language, text=data.text)
    raw = await _call_inference({**p, "max_tokens": 1024})
    return _build_response(raw, data.target_locale)
