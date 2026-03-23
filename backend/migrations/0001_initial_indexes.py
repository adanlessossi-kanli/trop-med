"""Migration 0001: create initial collection indexes."""
from motor.motor_asyncio import AsyncIOMotorDatabase

VERSION: int = 1
NAME: str = "initial_indexes"


async def up(db: AsyncIOMotorDatabase) -> None:
    await db["users"].create_index("email", unique=True)
    await db["patients"].create_index("fhir_id")
    await db["patients"].create_index("name_text")
    await db["encounters"].create_index("patient_id")
    await db["observations"].create_index([("patient_id", 1), ("code", 1)])
    await db["conditions"].create_index("patient_id")
    await db["medications"].create_index("patient_id")
    await db["conversations"].create_index("user_id")
    await db["files"].create_index("patient_id")
    await db["audit_logs"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["surveillance"].create_index([("region", 1), ("disease_code", 1), ("date", 1)])
