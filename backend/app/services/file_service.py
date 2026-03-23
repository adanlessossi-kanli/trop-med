import uuid
from datetime import datetime, timezone
import boto3
from app.core.config import get_settings
from app.core.database import get_db

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/dicom", "text/csv"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

db = get_db


def _s3_client():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("s3", **kwargs)


async def upload_file(file_bytes: bytes, filename: str, content_type: str, patient_id: str, encounter_id: str, user_id: str) -> dict:
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {content_type}")
    if len(file_bytes) > MAX_SIZE:
        raise ValueError("File exceeds 50 MB limit")

    file_id = str(uuid.uuid4())
    s3_key = f"patients/{patient_id}/{file_id}/{filename}"
    _s3_client().put_object(Bucket=get_settings().aws_s3_bucket, Key=s3_key, Body=file_bytes, ContentType=content_type)

    doc = {
        "_id": file_id,
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "filename": filename,
        "content_type": content_type,
        "size_bytes": len(file_bytes),
        "s3_key": s3_key,
        "uploaded_by": user_id,
        "created_at": datetime.now(timezone.utc),
        "deleted": False,
    }
    await db()["files"].insert_one(doc)
    return doc


async def get_download_url(file_id: str) -> str:
    meta = await db()["files"].find_one({"_id": file_id, "deleted": False})
    if not meta:
        raise ValueError("File not found")
    return _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": get_settings().aws_s3_bucket, "Key": meta["s3_key"]},
        ExpiresIn=3600,
    )


async def get_file_meta(file_id: str) -> dict | None:
    return await db()["files"].find_one({"_id": file_id, "deleted": False})


async def list_patient_files(patient_id: str) -> list:
    return await db()["files"].find({"patient_id": patient_id, "deleted": False}).to_list(100)


async def delete_file(file_id: str):
    await db()["files"].update_one({"_id": file_id}, {"$set": {"deleted": True}})
