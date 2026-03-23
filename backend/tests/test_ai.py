import pytest
from unittest.mock import AsyncMock, patch
from app.models.schemas import AIResponse


@pytest.mark.asyncio
async def test_ai_query(client, doctor_token):
    mock_response = AIResponse(answer="Test answer", confidence=0.9, sources=["src1"], locale="fr")
    with patch("app.services.ai_service.query", new_callable=AsyncMock, return_value=mock_response):
        resp = await client.post(
            "/api/v1/ai/query",
            json={"question": "What is malaria?", "context": {"locale": "fr"}},
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence"] == 0.9
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_ai_differential_forbidden_for_patient(client, patient_token):
    resp = await client.post(
        "/api/v1/ai/differential",
        json={"symptoms": ["fever"], "locale": "fr"},
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ai_low_confidence_warning(client, doctor_token):
    mock_response = AIResponse(answer="Uncertain", confidence=0.4, sources=[], disclaimer="⚠️ Faible confiance (40%). Ceci est généré par l'IA et doit être vérifié par un clinicien.", locale="fr")
    with patch("app.services.ai_service.query", new_callable=AsyncMock, return_value=mock_response):
        resp = await client.post(
            "/api/v1/ai/query",
            json={"question": "Rare condition?"},
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
        assert resp.status_code == 200
        assert "⚠️" in resp.json()["disclaimer"]
