"""
Patient CRUD endpoint tests.
Validates: Requirements 12.2
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import get_settings
from app.core.security import create_access_token

# Patch target: the route does `from app.services import patient_service`
_PATCH = "app.api.routes.patients.patient_service"
_AUDIT = "app.core.audit.log_audit"

MOCK_PATIENT = {
    "_id": "patient-123",
    "fhir_id": "fhir-456",
    "given_name": "Ama",
    "family_name": "Kofi",
    "name_text": "Ama Kofi",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "phone": "+228 90 00 00 00",
    "locale": "fr",
    "status": "active",
}

PATIENT_PAYLOAD = {
    "given_name": "Ama",
    "family_name": "Kofi",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "phone": "+228 90 00 00 00",
    "locale": "fr",
}


# ── Create ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_patient(client, doctor_token):
    with patch(f"{_PATCH}.create_patient", new_callable=AsyncMock) as mock_create, \
         patch(_AUDIT, new_callable=AsyncMock):
        mock_create.return_value = MOCK_PATIENT
        resp = await client.post(
            "/api/v1/patients",
            json=PATIENT_PAYLOAD,
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    assert resp.json()["given_name"] == "Ama"


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_patients_no_search(client, doctor_token):
    mock_result = {"items": [MOCK_PATIENT], "total": 1, "page": 1, "limit": 20}
    with patch(f"{_PATCH}.list_patients", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_result
        resp = await client.get(
            "/api/v1/patients",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_list_patients_with_search(client, doctor_token):
    mock_result = {"items": [MOCK_PATIENT], "total": 1, "page": 1, "limit": 20}
    with patch(f"{_PATCH}.list_patients", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_result
        resp = await client.get(
            "/api/v1/patients?q=Ama",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    mock_list.assert_called_once()
    call_kwargs = mock_list.call_args
    # q is the first positional arg
    assert call_kwargs.args[0] == "Ama"


# ── Get by ID ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_patient_found(client, doctor_token):
    with patch(f"{_PATCH}.get_patient", new_callable=AsyncMock) as mock_get, \
         patch(_AUDIT, new_callable=AsyncMock):
        mock_get.return_value = MOCK_PATIENT
        resp = await client.get(
            "/api/v1/patients/patient-123",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    assert resp.json()["_id"] == "patient-123"


@pytest.mark.asyncio
async def test_get_patient_not_found(client, doctor_token):
    with patch(f"{_PATCH}.get_patient", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = await client.get(
            "/api/v1/patients/nonexistent",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_patient(client, doctor_token):
    updated = {**MOCK_PATIENT, "phone": "+228 99 99 99 99"}
    with patch(f"{_PATCH}.update_patient", new_callable=AsyncMock) as mock_update, \
         patch(_AUDIT, new_callable=AsyncMock):
        mock_update.return_value = updated
        resp = await client.put(
            "/api/v1/patients/patient-123",
            json={"phone": "+228 99 99 99 99"},
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    assert resp.json()["phone"] == "+228 99 99 99 99"


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_patient_admin_allowed(client, admin_token):
    with patch(f"{_PATCH}.delete_patient", new_callable=AsyncMock), \
         patch(_AUDIT, new_callable=AsyncMock):
        resp = await client.delete(
            "/api/v1/patients/patient-123",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}


@pytest.mark.asyncio
async def test_delete_patient_nurse_forbidden(client):
    nurse_token = create_access_token("nurse-id", "nurse", "fr", get_settings())
    resp = await client.delete(
        "/api/v1/patients/patient-123",
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert resp.status_code == 403


# ── Role enforcement ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_patients_patient_role_forbidden(client, patient_token):
    resp = await client.get(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert resp.status_code == 403
