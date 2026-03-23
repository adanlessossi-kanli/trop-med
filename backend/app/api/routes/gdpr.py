from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.models.schemas import Consent, PatientConsent
from app.services import consent_service

router = APIRouter(prefix="/patients", tags=["gdpr"])


class UpdateConsentResponse(BaseModel):
    updated: bool


@router.get(
    "/{patient_id}/consents",
    response_model=PatientConsent,
    summary="Get consent records for a patient",
    description=(
        "Retrieve all GDPR consent records for the specified patient. "
        "Returns an empty consent list if no records exist yet."
    ),
)
async def get_consents(patient_id: str, user: Annotated[dict, Depends(get_current_user)]):
    return await consent_service.get_consents(patient_id) or {"patient_id": patient_id, "consents": []}


@router.put(
    "/{patient_id}/consents",
    response_model=UpdateConsentResponse,
    summary="Update a consent record for a patient",
    description=(
        "Create or update a GDPR consent entry for the specified patient. "
        "The update is recorded in the audit log."
    ),
)
async def update_consent(
    patient_id: str,
    consent: Consent,
    user: Annotated[dict, Depends(get_current_user)],
    request: Request,
):
    await consent_service.update_consent(patient_id, consent)
    await log_audit(user["sub"], user["role"], "UPDATE", "consent", patient_id, request)
    return {"updated": True}


@router.get(
    "/{patient_id}/export",
    summary="Export all data for a patient (GDPR right of access)",
    description=(
        "Export a complete copy of all personal data held for the specified patient, "
        "in compliance with GDPR Article 15 (right of access). "
        "Restricted to admin, doctor, and patient roles. The export is recorded in the audit log."
    ),
)
async def export_data(
    patient_id: str,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor", "patient"))],
    request: Request,
):
    data = await consent_service.export_patient_data(patient_id)
    await log_audit(user["sub"], user["role"], "EXPORT", "patient", patient_id, request, phi_accessed=True)
    return data
