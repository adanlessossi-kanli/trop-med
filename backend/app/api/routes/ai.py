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


@router.post(
    "/query",
    response_model=AIResponse,
    summary="Ask the AI assistant a clinical question",
    description=(
        "Submit a free-text clinical question to the AI assistant. "
        "The response includes an answer, a confidence score, and source references. "
        "A low confidence score (< 0.5) triggers a disclaimer warning. "
        "The query is recorded in the audit log. Available to all authenticated users."
    ),
)
async def ai_query(data: AIQueryRequest, user: Annotated[dict, Depends(get_current_user)], request: Request):
    result = await ai_service.query(data)
    await log_audit(
        user["sub"], user["role"], "AI_QUERY", "ai",
        details={"question": data.question[:200]}, request=request,
    )
    return result


@router.post(
    "/differential",
    response_model=AIResponse,
    summary="Generate a differential diagnosis",
    description=(
        "Provide symptoms, vitals, demographics, and history to receive an AI-generated differential diagnosis. "
        "Restricted to admin and doctor roles. The query is recorded in the audit log."
    ),
)
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


@router.post(
    "/literature",
    response_model=AIResponse,
    summary="Search medical literature",
    description=(
        "Search and summarise relevant medical literature for a given topic. "
        "Restricted to admin, doctor, and researcher roles. The query is recorded in the audit log."
    ),
)
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


@router.post(
    "/translate",
    response_model=AIResponse,
    summary="Translate clinical text",
    description=(
        "Translate a piece of clinical text into the specified target locale (fr or en). "
        "Available to all authenticated users."
    ),
)
async def ai_translate(data: AITranslateRequest, user: Annotated[dict, Depends(get_current_user)]):
    return await ai_service.translate(data)
