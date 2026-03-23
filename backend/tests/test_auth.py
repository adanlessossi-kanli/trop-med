"""
Comprehensive auth endpoint tests.
Validates: Requirements 12.1
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.core.security import create_refresh_token
from app.models.schemas import UserOut

# The route does `from app.services import auth_service` and calls
# `auth_service.<func>(...)`, so we patch via the route module's reference.
_PATCH = "app.api.routes.auth.auth_service"


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client):
    user_out = UserOut(
        id="new-user-id",
        email="newuser@example.com",
        full_name="New User",
        role="patient",
        locale="fr",
    )
    with patch(f"{_PATCH}.register", new_callable=AsyncMock) as mock_register:
        mock_register.return_value = user_out
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "secret123",
                "full_name": "New User",
                "role": "patient",
                "locale": "fr",
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "patient"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    with patch(f"{_PATCH}.register", new_callable=AsyncMock) as mock_register:
        mock_register.side_effect = ValueError("Email already registered")
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "secret123",
                "full_name": "Existing User",
                "role": "patient",
                "locale": "fr",
            },
        )
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["error"]["message"]


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_valid_credentials(client):
    tokens = {
        "access_token": "access.token.here",
        "refresh_token": "refresh.token.here",
        "token_type": "bearer",
    }
    with patch(f"{_PATCH}.login", new_callable=AsyncMock) as mock_login:
        mock_login.return_value = tokens
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "correct_password"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    with patch(f"{_PATCH}.login", new_callable=AsyncMock) as mock_login:
        mock_login.side_effect = ValueError("Invalid credentials")
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "wrong_password"},
        )
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_login_inactive_account(client):
    # The service filters by is_active=True in the DB query, so inactive users
    # get the same "Invalid credentials" error as wrong passwords.
    with patch(f"{_PATCH}.login", new_callable=AsyncMock) as mock_login:
        mock_login.side_effect = ValueError("Invalid credentials")
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "any_password"},
        )
    assert resp.status_code == 401
    assert resp.json()["error"]["message"] == "Invalid credentials"


# ── Refresh ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_valid_token(client, settings):
    refresh_tok = create_refresh_token("test-doctor-id", settings)
    new_tokens = {
        "access_token": "new.access.token",
        "refresh_token": "new.refresh.token",
        "token_type": "bearer",
    }
    with patch(f"{_PATCH}.refresh", new_callable=AsyncMock) as mock_refresh:
        mock_refresh.return_value = new_tokens
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_tok},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_expired_or_invalid_token(client):
    with patch(f"{_PATCH}.refresh", new_callable=AsyncMock) as mock_refresh:
        mock_refresh.side_effect = ValueError("Invalid refresh token")
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "totally.invalid.token"},
        )
    assert resp.status_code == 401
    assert "Invalid refresh token" in resp.json()["error"]["message"]


# ── Logout ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logout(client, doctor_token):
    with patch("app.core.audit.log_audit", new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged out"}


@pytest.mark.asyncio
async def test_logout_no_token(client):
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 403


# ── MFA Setup ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mfa_setup(client, doctor_token):
    mfa_data = {
        "secret": "BASE32SECRET",
        "qr_uri": "otpauth://totp/Trop-Med:test-doctor-id?secret=BASE32SECRET",
    }
    with patch(f"{_PATCH}.setup_mfa", new_callable=AsyncMock) as mock_setup:
        mock_setup.return_value = mfa_data
        resp = await client.post(
            "/api/v1/auth/mfa/setup",
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "secret" in data
    assert "qr_uri" in data


@pytest.mark.asyncio
async def test_mfa_setup_no_token(client):
    resp = await client.post("/api/v1/auth/mfa/setup")
    assert resp.status_code == 403


# ── MFA Verify ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mfa_verify_valid_code(client, doctor_token):
    with patch(f"{_PATCH}.verify_mfa", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = True
        resp = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": "123456"},
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"verified": True}


@pytest.mark.asyncio
async def test_mfa_verify_invalid_code(client, doctor_token):
    with patch(f"{_PATCH}.verify_mfa", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = False
        resp = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": "000000"},
            headers={"Authorization": f"Bearer {doctor_token}"},
        )
    assert resp.status_code == 400
    assert "Invalid MFA code" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_mfa_verify_no_token(client):
    resp = await client.post("/api/v1/auth/mfa/verify", json={"code": "123456"})
    assert resp.status_code == 403
