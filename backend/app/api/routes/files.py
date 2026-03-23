from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.audit import log_audit
from app.core.security import RoleRequired, get_current_user
from app.services import file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    patient_id: str = Form(""),
    encounter_id: str = Form(""),
    user: dict = Depends(RoleRequired("admin", "doctor", "nurse", "patient")),
    request: Request = None,
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


@router.get("/{file_id}")
async def get_meta(file_id: str, user: Annotated[dict, Depends(get_current_user)]):
    meta = await file_service.get_file_meta(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    return meta


@router.get("/{file_id}/download")
async def download(file_id: str, user: Annotated[dict, Depends(get_current_user)]):
    try:
        url = await file_service.get_download_url(file_id)
        return {"download_url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete("/{file_id}")
async def delete(file_id: str, user: Annotated[dict, Depends(RoleRequired("admin", "doctor"))], request: Request):
    await file_service.delete_file(file_id)
    await log_audit(user["sub"], user["role"], "DELETE", "file", file_id, request)
    return {"deleted": True}
