from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.models.schemas import PatientCreate
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])

clinician = RoleRequired("admin", "doctor", "nurse")


@router.get("")
async def list_patients(
    user: Annotated[dict, Depends(clinician)],
    q: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = "active",
):
    return await patient_service.list_patients(q, page, limit, status)


@router.post("")
async def create_patient(data: PatientCreate, user: Annotated[dict, Depends(clinician)], request: Request):
    patient = await patient_service.create_patient(data)
    await log_audit(user["sub"], user["role"], "CREATE", "patient", patient["_id"], request, phi_accessed=True)
    return patient


@router.get("/{patient_id}")
async def get_patient(patient_id: str, user: Annotated[dict, Depends(get_current_user)], request: Request):
    patient = await patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await log_audit(user["sub"], user["role"], "READ", "patient", patient_id, request, phi_accessed=True)
    return patient


@router.put("/{patient_id}")
async def update_patient(patient_id: str, data: dict, user: Annotated[dict, Depends(clinician)], request: Request):
    patient = await patient_service.update_patient(patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await log_audit(user["sub"], user["role"], "UPDATE", "patient", patient_id, request, phi_accessed=True)
    return patient


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    user: Annotated[dict, Depends(RoleRequired("admin", "doctor"))],
    request: Request,
):
    await patient_service.delete_patient(patient_id)
    await log_audit(user["sub"], user["role"], "DELETE", "patient", patient_id, request, phi_accessed=True)
    return {"deleted": True}


@router.get("/{patient_id}/timeline")
async def get_timeline(patient_id: str, user: Annotated[dict, Depends(clinician)]):
    return await patient_service.get_timeline(patient_id)
