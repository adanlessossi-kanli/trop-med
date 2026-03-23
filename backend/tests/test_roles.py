"""Role-based access control tests for key API endpoints.

Validates: Requirements 12.3, 12.4
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.schemas import AIResponse

_settings = get_settings()
nurse_token = create_access_token("nurse-id", "nurse", "fr", _settings)
researcher_token = create_access_token("researcher-id", "researcher", "fr", _settings)


# ── /patients ──────────────────────────────────────────────────────────────

PATIENTS_MOCK = {"items": [], "total": 0, "page": 1, "limit": 20}
PATIENTS_PATH = "app.api.routes.patients.patient_service.list_patients"


@pytest.mark.asyncio
async def test_patients_admin_allowed(client, admin_token):
    with patch(PATIENTS_PATH, new_callable=AsyncMock, return_value=PATIENTS_MOCK):
        resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_patients_doctor_allowed(client, doctor_token):
    with patch(PATIENTS_PATH, new_callable=AsyncMock, return_value=PATIENTS_MOCK):
        resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_patients_nurse_allowed(client):
    with patch(PATIENTS_PATH, new_callable=AsyncMock, return_value=PATIENTS_MOCK):
        resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {nurse_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_patients_researcher_forbidden(client):
    resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {researcher_token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_patients_patient_forbidden(client, patient_token):
    resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 403


# ── /fhir/Encounter ────────────────────────────────────────────────────────

CLINICAL_PATH = "app.api.routes.clinical.clinical_service.list_resources"


@pytest.mark.asyncio
async def test_clinical_admin_allowed(client, admin_token):
    with patch(CLINICAL_PATH, new_callable=AsyncMock, return_value=[]):
        resp = await client.get("/api/v1/fhir/Encounter", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_clinical_doctor_allowed(client, doctor_token):
    with patch(CLINICAL_PATH, new_callable=AsyncMock, return_value=[]):
        resp = await client.get("/api/v1/fhir/Encounter", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_clinical_nurse_allowed(client):
    with patch(CLINICAL_PATH, new_callable=AsyncMock, return_value=[]):
        resp = await client.get("/api/v1/fhir/Encounter", headers={"Authorization": f"Bearer {nurse_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_clinical_researcher_forbidden(client):
    resp = await client.get("/api/v1/fhir/Encounter", headers={"Authorization": f"Bearer {researcher_token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_clinical_patient_forbidden(client, patient_token):
    resp = await client.get("/api/v1/fhir/Encounter", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 403


# ── /ai/differential ───────────────────────────────────────────────────────

AI_DIFF_PATH = "app.api.routes.ai.ai_service.differential"
AI_DIFF_BODY = {"symptoms": ["fever", "headache"], "locale": "fr"}
_ai_mock_response = AIResponse(
    answer="Test", confidence=0.9, sources=["src1"],
    disclaimer="Ceci est généré par l'IA et doit être vérifié par un clinicien.",
    locale="fr",
)


@pytest.mark.asyncio
async def test_ai_differential_doctor_allowed(client, doctor_token):
    with patch(AI_DIFF_PATH, new_callable=AsyncMock, return_value=_ai_mock_response):
        resp = await client.post(
            "/api/v1/ai/differential",
            json=AI_DIFF_BODY,
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_differential_admin_allowed(client, admin_token):
    with patch(AI_DIFF_PATH, new_callable=AsyncMock, return_value=_ai_mock_response):
        resp = await client.post(
            "/api/v1/ai/differential",
            json=AI_DIFF_BODY,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_differential_nurse_forbidden(client):
    resp = await client.post(
        "/api/v1/ai/differential",
        json=AI_DIFF_BODY,
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ai_differential_researcher_forbidden(client):
    resp = await client.post(
        "/api/v1/ai/differential",
        json=AI_DIFF_BODY,
        headers={"Authorization": f"Bearer {researcher_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ai_differential_patient_forbidden(client, patient_token):
    resp = await client.post(
        "/api/v1/ai/differential",
        json=AI_DIFF_BODY,
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert resp.status_code == 403


# ── /surveillance/dashboard ────────────────────────────────────────────────

SURV_PATH = "app.api.routes.surveillance.surveillance_service.get_dashboard"
SURV_MOCK = {"aggregations": []}


@pytest.mark.asyncio
async def test_surveillance_admin_allowed(client, admin_token):
    with patch(SURV_PATH, new_callable=AsyncMock, return_value=SURV_MOCK):
        resp = await client.get("/api/v1/surveillance/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_surveillance_doctor_allowed(client, doctor_token):
    with patch(SURV_PATH, new_callable=AsyncMock, return_value=SURV_MOCK):
        resp = await client.get("/api/v1/surveillance/dashboard", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_surveillance_researcher_allowed(client):
    with patch(SURV_PATH, new_callable=AsyncMock, return_value=SURV_MOCK):
        resp = await client.get(
            "/api/v1/surveillance/dashboard",
            headers={"Authorization": f"Bearer {researcher_token}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_surveillance_nurse_forbidden(client):
    resp = await client.get("/api/v1/surveillance/dashboard", headers={"Authorization": f"Bearer {nurse_token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_surveillance_patient_forbidden(client, patient_token):
    resp = await client.get("/api/v1/surveillance/dashboard", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 403


# ── /patients/{id}/consents ────────────────────────────────────────────────

CONSENT_PATH = "app.api.routes.gdpr.consent_service.get_consents"
CONSENT_MOCK = {"patient_id": "p1", "consents": []}


@pytest.mark.asyncio
async def test_gdpr_consents_admin_allowed(client, admin_token):
    with patch(CONSENT_PATH, new_callable=AsyncMock, return_value=CONSENT_MOCK):
        resp = await client.get("/api/v1/patients/p1/consents", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_gdpr_consents_doctor_allowed(client, doctor_token):
    with patch(CONSENT_PATH, new_callable=AsyncMock, return_value=CONSENT_MOCK):
        resp = await client.get("/api/v1/patients/p1/consents", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_gdpr_consents_nurse_allowed(client):
    with patch(CONSENT_PATH, new_callable=AsyncMock, return_value=CONSENT_MOCK):
        resp = await client.get("/api/v1/patients/p1/consents", headers={"Authorization": f"Bearer {nurse_token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_gdpr_consents_researcher_allowed(client):
    with patch(CONSENT_PATH, new_callable=AsyncMock, return_value=CONSENT_MOCK):
        resp = await client.get(
            "/api/v1/patients/p1/consents",
            headers={"Authorization": f"Bearer {researcher_token}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_gdpr_consents_patient_allowed(client, patient_token):
    with patch(CONSENT_PATH, new_callable=AsyncMock, return_value=CONSENT_MOCK):
        resp = await client.get("/api/v1/patients/p1/consents", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 200
