import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_patient(client, doctor_token):
    patient_data = {
        "given_name": "Ama", "family_name": "Doe", "date_of_birth": "1990-01-01",
        "gender": "female", "phone": "+228 90 00 00 00", "locale": "fr",
    }
    mock_doc = {"_id": "p1", "fhir_id": "f1", **patient_data, "name_text": "Ama Doe", "status": "active"}
    with patch("app.services.patient_service.create_patient", new_callable=AsyncMock, return_value=mock_doc):
        resp = await client.post("/api/v1/patients", json=patient_data, headers={"Authorization": f"Bearer {doctor_token}"})
        assert resp.status_code == 200
        assert resp.json()["given_name"] == "Ama"


@pytest.mark.asyncio
async def test_get_patient_not_found(client, doctor_token):
    with patch("app.services.patient_service.get_patient", new_callable=AsyncMock, return_value=None):
        resp = await client.get("/api/v1/patients/nonexistent", headers={"Authorization": f"Bearer {doctor_token}"})
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_patient_nurse_forbidden(client):
    from app.core.security import create_access_token
    from app.core.config import get_settings
    nurse_token = create_access_token("nurse-id", "nurse", "fr", get_settings())
    resp = await client.delete("/api/v1/patients/p1", headers={"Authorization": f"Bearer {nurse_token}"})
    assert resp.status_code == 403


def test_password_hashing():
    from app.core.security import hash_password, verify_password
    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    from app.core.security import create_access_token, decode_token
    from app.core.config import get_settings
    settings = get_settings()
    token = create_access_token("u1", "doctor", "fr", settings)
    payload = decode_token(token, settings)
    assert payload["sub"] == "u1"
    assert payload["role"] == "doctor"
