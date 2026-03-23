import uuid
from datetime import UTC, datetime

from app.core.database import get_db
from app.models.schemas import ConditionCreate, EncounterCreate, MedicationCreate, ObservationCreate

db = get_db


async def _insert(collection: str, data: dict) -> dict:
    data["_id"] = str(uuid.uuid4())
    data["date"] = datetime.now(UTC)
    await db()[collection].insert_one(data)
    return data


async def create_encounter(data: EncounterCreate) -> dict:
    return await _insert("encounters", data.model_dump())


async def create_observation(data: ObservationCreate) -> dict:
    return await _insert("observations", data.model_dump())


async def create_condition(data: ConditionCreate) -> dict:
    return await _insert("conditions", data.model_dump())


async def create_medication(data: MedicationCreate) -> dict:
    return await _insert("medications", data.model_dump())


async def get_resource(collection: str, resource_id: str) -> dict | None:
    return await db()[collection].find_one({"_id": resource_id})


async def update_resource(collection: str, resource_id: str, data: dict) -> dict | None:
    return await db()[collection].find_one_and_update(
        {"_id": resource_id}, {"$set": data}, return_document=True
    )


async def list_resources(collection: str, patient_id: str = "", limit: int = 50) -> list:
    query = {"patient_id": patient_id} if patient_id else {}
    return await db()[collection].find(query).sort("date", -1).to_list(limit)
