import uuid
from datetime import UTC, datetime

from app.core.database import get_db
from app.models.schemas import PatientCreate

db = get_db


async def create_patient(data: PatientCreate) -> dict:
    doc = {
        "_id": str(uuid.uuid4()),
        "fhir_id": str(uuid.uuid4()),
        **data.model_dump(),
        "name_text": f"{data.given_name} {data.family_name}",
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    await db()["patients"].insert_one(doc)
    return doc


async def get_patient(patient_id: str) -> dict | None:
    return await db()["patients"].find_one({"_id": patient_id, "status": {"$ne": "deleted"}})


async def list_patients(q: str = "", page: int = 1, limit: int = 20, status: str = "active") -> dict:
    coll = db()["patients"]
    query: dict = {"status": status}
    if q:
        query["name_text"] = {"$regex": q, "$options": "i"}
    skip = (page - 1) * limit
    cursor = coll.find(query).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await coll.count_documents(query)
    return {"items": items, "total": total, "page": page, "limit": limit}


async def update_patient(patient_id: str, data: dict) -> dict | None:
    data["updated_at"] = datetime.now(UTC)
    result = await db()["patients"].find_one_and_update(
        {"_id": patient_id}, {"$set": data}, return_document=True
    )
    return result


async def delete_patient(patient_id: str):
    await db()["patients"].update_one({"_id": patient_id}, {"$set": {"status": "deleted"}})


async def get_timeline(patient_id: str) -> dict:
    d = db()
    encounters = await d["encounters"].find({"patient_id": patient_id}).sort("date", -1).to_list(100)
    observations = await d["observations"].find({"patient_id": patient_id}).sort("date", -1).to_list(100)
    conditions = await d["conditions"].find({"patient_id": patient_id}).to_list(100)
    medications = await d["medications"].find({"patient_id": patient_id}).to_list(100)
    return {
        "encounters": encounters,
        "observations": observations,
        "conditions": conditions,
        "medications": medications,
    }
