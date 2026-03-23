from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.models.schemas import PatientCreate, PatientInDB
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])

clinician = RoleRequired("admin", "doctor", "nurse")


class DeleteResponse(BaseModel):
    deleted: bool


@router.get(
    "",
    summary="List patients",
    description=(
        "Return a paginated list of patients. Supports full-text search via the `q` parameter "
        "and filtering by `status` (active / inactive). Requires clinician role."
    ),
)
async def list_patients(
    user: Annotated[dict, Depends(clinician)],
    q: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = "active",
):
    return await patient_service.list_patients(q, page, limit, status)


@router.post(
    "",
    response_model=PatientInDB,
    summary="Create a new patient",
    description=(
        "Register a new patient record. The action is recorded in the audit log as a PHI access event. "
        "Requires clinician role."
    ),
)
async def create_patient(data: PatientCreate, user: Annotated[dict, Depends(clinician)], request: Request):
    patient = await patient_service.create_patient(data)
    await log_audit(user["sub"], user["role"], "CREATE", "patient", patient["_id"], request, phi_accessed=True)
    return patient


@router.get(
    "/{patient_id}",
    response_model=PatientInDB,
    summary="Get a patient by ID",
    description=(
        "Retrieve a single patient record by its unique identifier. "
        "Returns 404 if the patient does not exist. Access is recorded in the audit log."
    ),
)
async def get_patient(patient_id: str, user: Annotated[dict, Depends(get_current_user)], request: Request):
    patient = await patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await log_audit(user["sub"], user["role"], "READ", "patient", patient_id, request, phi_accessed=True)
    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientInDB,
    summary="Update a patient record",
    description=(
        "Apply a partial update to an existing patient record. "
        "Returns 404 if the patient does not exist. Requires clinician role."
    ),
)
async def update_patient(patient_id: str, data: dict, user: Annotated[dict, Depends(clinician)], request: Request):
    patient = await patient_service.update_patient(patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await log_audit(user["sub"], user["role"], "UPDATE", "patient", patient_id, request, phi_accessed=True)
    return patient


@router.delete(
    "/{patient_id}",
    response_model=DeleteResponse,
    summary="Delete a patient record",
    description=(
        "Permanently remove a patient record. "
        "Restricted to admin and doctor roles. The deletion is recorded in the audit log."
    ),
)
async def delete_patient(
    patient_id: str,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor"))],
    request: Request,
):
    await patient_service.delete_patient(patient_id)
    await log_audit(user["sub"], user["role"], "DELETE", "patient", patient_id, request, phi_accessed=True)
    return {"deleted": True}


@router.get(
    "/{patient_id}/timeline",
    summary="Get patient clinical timeline",
    description=(
        "Return a chronological list of all clinical events (encounters, observations, conditions, medications) "
        "for the specified patient. Requires clinician role."
    ),
)
async def get_timeline(patient_id: str, user: Annotated[dict, Depends(clinician)]):
    return await patient_service.get_timeline(patient_id)
