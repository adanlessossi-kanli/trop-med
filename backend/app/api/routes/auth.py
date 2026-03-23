from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.audit import log_audit
from app.core.config import Settings, get_settings
from app.core.security import get_current_user
from app.models.schemas import UserCreate, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str


class MFASetupResponse(BaseModel):
    secret: str
    qr_uri: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFAVerifyResponse(BaseModel):
    verified: bool


@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="Create a new user account with the provided credentials and role. Returns the created user profile.",
)
async def register(data: UserCreate):
    try:
        return await auth_service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and obtain tokens",
    description=(
        "Validate email and password credentials. Returns a short-lived access token (15 min) "
        "and a long-lived refresh token (7 days). If MFA is enabled the response will indicate "
        "that a TOTP code is required."
    ),
)
async def login(data: LoginRequest, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        tokens = await auth_service.login(data.email, data.password, settings)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access token",
    description=(
        "Exchange a valid refresh token for a new access token and refresh token pair. "
        "The old refresh token is invalidated after use."
    ),
)
async def refresh(data: RefreshRequest, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        return await auth_service.refresh(data.refresh_token, settings)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Invalidate the current session",
    description="Log out the authenticated user and record the logout event in the audit log.",
)
async def logout(user: Annotated[dict, Depends(get_current_user)]):
    await log_audit(user["sub"], user["role"], "LOGOUT", "session")
    return {"message": "Logged out"}


@router.post(
    "/mfa/setup",
    response_model=MFASetupResponse,
    summary="Initialise MFA for the current user",
    description=(
        "Generate a TOTP secret and QR-code URI for the authenticated user. "
        "The user must scan the QR code with an authenticator app and then verify "
        "a code via POST /auth/mfa/verify to activate MFA."
    ),
)
async def mfa_setup(user: Annotated[dict, Depends(get_current_user)]):
    return await auth_service.setup_mfa(user["sub"])


@router.post(
    "/mfa/verify",
    response_model=MFAVerifyResponse,
    summary="Verify a TOTP code and activate MFA",
    description=(
        "Validate the 6-digit TOTP code provided by the user's authenticator app. "
        "On success, MFA is marked as active on the account."
    ),
)
async def mfa_verify(data: MFAVerifyRequest, user: Annotated[dict, Depends(get_current_user)]):
    ok = await auth_service.verify_mfa(user["sub"], data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    return {"verified": True}
