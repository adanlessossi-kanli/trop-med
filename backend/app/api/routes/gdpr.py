from typing import Annotated
from fastapi import APIRouter, Depends, Request

from app.core.security import get_current_user, RoleRequired
from app.core.audit import log_audit
from app.models.schemas import Consent
from app.services import consent_service

router = APIRouter(prefix="/patients", tags=["gdpr"])


@router.get("/{patient_id}/consents")
async def get_consents(patient_id: str, user: Annotated[dict, Depends(get_current_user)]):
    return await consent_service.get_consents(patient_id) or {"patient_id": patient_id, "consents": []}


@router.put("/{patient_id}/consents")
async def update_consent(patient_id: str, consent: Consent, user: Annotated[dict, Depends(get_current_user)], request: Request):
    await consent_service.update_consent(patient_id, consent)
    await log_audit(user["sub"], user["role"], "UPDATE", "consent", patient_id, request)
    return {"updated": True}


@router.get("/{patient_id}/export")
async def export_data(
    patient_id: str,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor", "patient"))],
    request: Request,
):
    data = await consent_service.export_patient_data(patient_id)
    await log_audit(user["sub"], user["role"], "EXPORT", "patient", patient_id, request, phi_accessed=True)
    return data
