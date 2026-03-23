from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.security import RoleRequired
from app.services import file_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/files")
async def patient_files(patient_id: str, user: Annotated[dict, Depends(RoleRequired("admin", "doctor", "nurse"))]):
    return await file_service.list_patient_files(patient_id)
