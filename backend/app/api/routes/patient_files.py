from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core.security import RoleRequired
from app.models.schemas import FileMetadata
from app.services import file_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get(
    "/{patient_id}/files",
    response_model=List[FileMetadata],
    summary="List files attached to a patient",
    description=(
        "Return all file metadata records associated with the specified patient. "
        "Restricted to admin, doctor, and nurse roles."
    ),
)
async def patient_files(patient_id: str, user: Annotated[dict, Depends(RoleRequired("admin", "doctor", "nurse"))]):
    return await file_service.list_patient_files(patient_id)
