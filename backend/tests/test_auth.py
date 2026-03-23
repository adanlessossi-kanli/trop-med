from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_login_invalid(client):
    resp = await client.post("/api/v1/auth/login", json={"email": "bad@test.com", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_no_token(client):
    resp = await client.get("/api/v1/patients")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_protected_route_with_token(client, doctor_token):
    with patch("app.services.patient_service.list_patients", new_callable=AsyncMock) as mock:
        mock.return_value = {"items": [], "total": 0, "page": 1, "limit": 20}
        resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {doctor_token}"})
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_forbidden_role(client, patient_token):
    resp = await client.get("/api/v1/patients", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 403
