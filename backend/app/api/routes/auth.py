from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.models.schemas import UserCreate, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MFAVerifyRequest(BaseModel):
    code: str


@router.post("/register", response_model=UserOut)
async def register(data: UserCreate):
    try:
        return await auth_service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(data: LoginRequest, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        tokens = await auth_service.login(data.email, data.password, settings)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
async def refresh(data: RefreshRequest, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        return await auth_service.refresh(data.refresh_token, settings)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(user: Annotated[dict, Depends(get_current_user)]):
    await log_audit(user["sub"], user["role"], "LOGOUT", "session")
    return {"message": "Logged out"}


@router.post("/mfa/setup")
async def mfa_setup(user: Annotated[dict, Depends(get_current_user)]):
    return await auth_service.setup_mfa(user["sub"])


@router.post("/mfa/verify")
async def mfa_verify(data: MFAVerifyRequest, user: Annotated[dict, Depends(get_current_user)]):
    ok = await auth_service.verify_mfa(user["sub"], data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    return {"verified": True}
