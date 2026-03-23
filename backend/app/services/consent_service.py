from datetime import UTC, datetime

from app.core.database import get_db
from app.models.schemas import Consent

db = get_db


async def get_consents(patient_id: str) -> dict | None:
    return await db()["consents"].find_one({"patient_id": patient_id})


async def update_consent(patient_id: str, consent: Consent):
    await db()["consents"].update_one(
        {"patient_id": patient_id, "consents.type": consent.type},
        {"$set": {"consents.$": consent.model_dump()}},
    )
    # If the consent type didn't exist yet, push it
    result = await db()["consents"].update_one(
        {"patient_id": patient_id, "consents.type": {"$ne": consent.type}},
        {"$push": {"consents": consent.model_dump()}},
    )
    if result.matched_count == 0:
        await db()["consents"].update_one(
            {"patient_id": patient_id},
            {"$setOnInsert": {"patient_id": patient_id, "consents": [consent.model_dump()]}},
            upsert=True,
        )


async def export_patient_data(patient_id: str) -> dict:
    d = db()
    patient = await d["patients"].find_one({"_id": patient_id})
    encounters = await d["encounters"].find({"patient_id": patient_id}).to_list(500)
    observations = await d["observations"].find({"patient_id": patient_id}).to_list(500)
    conditions = await d["conditions"].find({"patient_id": patient_id}).to_list(500)
    medications = await d["medications"].find({"patient_id": patient_id}).to_list(500)
    files = await d["files"].find({"patient_id": patient_id, "deleted": False}).to_list(500)
    conversations = await d["conversations"].find({"user_id": patient_id}).to_list(500)
    consents = await d["consents"].find_one({"patient_id": patient_id})

    return {
        "patient": patient,
        "encounters": encounters,
        "observations": observations,
        "conditions": conditions,
        "medications": medications,
        "files_metadata": files,
        "conversations": conversations,
        "consents": consents,
        "exported_at": datetime.now(UTC).isoformat(),
    }
