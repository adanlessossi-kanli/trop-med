from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.models.schemas import FileMetadata
from app.services import file_service

router = APIRouter(prefix="/files", tags=["files"])


class DeleteResponse(BaseModel):
    deleted: bool


class DownloadResponse(BaseModel):
    download_url: str


@router.post(
    "/upload",
    response_model=FileMetadata,
    summary="Upload a file",
    description=(
        "Upload a binary file and associate it with an optional patient and encounter. "
        "The file is stored in S3-compatible object storage. "
        "Returns the file metadata record including the generated file ID. "
        "Restricted to admin, doctor, nurse, and patient roles."
    ),
)
async def upload(
    request: Request,
    file: UploadFile = File(...),
    patient_id: str = Form(""),
    encounter_id: str = Form(""),
    user: dict = Depends(RoleRequired("admin", "doctor", "nurse", "patient")),
):
    content = await file.read()
    try:
        meta = await file_service.upload_file(
            content, file.filename or "file",
            file.content_type or "", patient_id, encounter_id, user["sub"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    await log_audit(user["sub"], user["role"], "CREATE", "file", meta["_id"], request)
    return meta


@router.get(
    "/{file_id}",
    response_model=FileMetadata,
    summary="Get file metadata",
    description=(
        "Retrieve the metadata record for a stored file by its unique identifier. "
        "Returns 404 if the file does not exist or has been deleted."
    ),
)
async def get_meta(file_id: str, user: Annotated[dict, Depends(get_current_user)]):
    meta = await file_service.get_file_meta(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    return meta


@router.get(
    "/{file_id}/download",
    response_model=DownloadResponse,
    summary="Get a pre-signed download URL",
    description=(
        "Generate a time-limited pre-signed URL for downloading the specified file directly from object storage. "
        "Returns 404 if the file does not exist."
    ),
)
async def download(file_id: str, user: Annotated[dict, Depends(get_current_user)]):
    try:
        url = await file_service.get_download_url(file_id)
        return {"download_url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/{file_id}",
    response_model=DeleteResponse,
    summary="Delete a file",
    description=(
        "Permanently delete a file and its metadata record. "
        "Restricted to admin and doctor roles. The deletion is recorded in the audit log."
    ),
)
async def delete(file_id: str, user: Annotated[dict, Depends(RoleRequired("admin", "doctor"))], request: Request):
    await file_service.delete_file(file_id)
    await log_audit(user["sub"], user["role"], "DELETE", "file", file_id, request)
    return {"deleted": True}
