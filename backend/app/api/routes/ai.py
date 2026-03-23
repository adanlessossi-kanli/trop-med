from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.models.schemas import (
    AIDifferentialRequest,
    AILiteratureRequest,
    AIQueryRequest,
    AIResponse,
    AITranslateRequest,
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/query", response_model=AIResponse)
async def ai_query(data: AIQueryRequest, user: Annotated[dict, Depends(get_current_user)], request: Request):
    result = await ai_service.query(data)
    await log_audit(
        user["sub"], user["role"], "AI_QUERY", "ai",
        details={"question": data.question[:200]}, request=request,
    )
    return result


@router.post("/differential", response_model=AIResponse)
async def ai_differential(
    data: AIDifferentialRequest,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor"))],
    request: Request,
):
    result = await ai_service.differential(data)
    await log_audit(
        user["sub"], user["role"], "AI_QUERY", "ai",
        details={"type": "differential"}, request=request,
    )
    return result


@router.post("/literature", response_model=AIResponse)
async def ai_literature(
    data: AILiteratureRequest,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor", "researcher"))],
    request: Request,
):
    result = await ai_service.literature(data)
    await log_audit(
        user["sub"], user["role"], "AI_QUERY", "ai",
        details={"type": "literature"}, request=request,
    )
    return result


@router.post("/translate", response_model=AIResponse)
async def ai_translate(data: AITranslateRequest, user: Annotated[dict, Depends(get_current_user)]):
    return await ai_service.translate(data)
