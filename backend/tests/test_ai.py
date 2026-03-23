"""AI endpoint tests with extended coverage.

Validates: Requirements 12.3, 12.4
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.models.schemas import AIResponse


def make_ai_response(confidence=0.9, answer="Test answer"):
    disclaimer = "Ceci est généré par l'IA et doit être vérifié par un clinicien."
    if confidence < 0.6:
        disclaimer = f"⚠️ Faible confiance ({confidence:.0%}). " + disclaimer
    return AIResponse(answer=answer, confidence=confidence, sources=["src1"], disclaimer=disclaimer, locale="fr")


@pytest.mark.asyncio
async def test_ai_query_high_confidence(client, doctor_token):
    with patch("app.api.routes.ai.ai_service.query", new_callable=AsyncMock, return_value=make_ai_response(0.9)):
        with patch("app.api.routes.ai.log_audit", new_callable=AsyncMock):
            resp = await client.post(
                "/api/v1/ai/query",
                json={"question": "What is malaria?", "context": {"locale": "fr"}},
                headers={"Authorization": f"Bearer {doctor_token}"},
            )
    assert resp.status_code == 200
    assert resp.json()["confidence"] == 0.9


@pytest.mark.asyncio
async def test_ai_query_low_confidence_warning(client, doctor_token):
    with patch("app.api.routes.ai.ai_service.query", new_callable=AsyncMock, return_value=make_ai_response(0.4)):
        with patch("app.api.routes.ai.log_audit", new_callable=AsyncMock):
            resp = await client.post(
                "/api/v1/ai/query",
                json={"question": "What is malaria?", "context": {"locale": "fr"}},
                headers={"Authorization": f"Bearer {doctor_token}"},
            )
    assert resp.status_code == 200
    assert "⚠️" in resp.json()["disclaimer"]


@pytest.mark.asyncio
async def test_ai_differential_doctor_allowed(client, doctor_token):
    with patch("app.api.routes.ai.ai_service.differential", new_callable=AsyncMock, return_value=make_ai_response()):
        with patch("app.api.routes.ai.log_audit", new_callable=AsyncMock):
            resp = await client.post(
                "/api/v1/ai/differential",
                json={"symptoms": ["fever", "headache"], "locale": "fr"},
                headers={"Authorization": f"Bearer {doctor_token}"},
            )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_differential_patient_forbidden(client, patient_token):
    resp = await client.post(
        "/api/v1/ai/differential",
        json={"symptoms": ["fever", "headache"], "locale": "fr"},
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ai_literature_search(client, doctor_token):
    with patch("app.api.routes.ai.ai_service.literature", new_callable=AsyncMock, return_value=make_ai_response()):
        with patch("app.api.routes.ai.log_audit", new_callable=AsyncMock):
            resp = await client.post(
                "/api/v1/ai/literature",
                json={"topic": "malaria treatment", "locale": "fr"},
                headers={"Authorization": f"Bearer {doctor_token}"},
            )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_query_no_token(client):
    resp = await client.post(
        "/api/v1/ai/query",
        json={"question": "What is malaria?", "context": {"locale": "fr"}},
    )
    assert resp.status_code == 403
