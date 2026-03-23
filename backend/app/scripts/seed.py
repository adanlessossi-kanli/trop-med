"""Seed script: python -m app.scripts.seed"""
import asyncio
import uuid
from datetime import datetime, timezone
from app.core.database import get_db, close_db
from app.core.security import hash_password


async def seed():
    db = get_db()

    # Users
    users = [
        {"_id": str(uuid.uuid4()), "email": "admin@tropmed.local", "hashed_password": hash_password("admin123"), "full_name": "Admin Trop-Med", "role": "admin", "locale": "fr", "mfa_enabled": False, "mfa_secret": None, "is_active": True},
        {"_id": str(uuid.uuid4()), "email": "doctor@tropmed.local", "hashed_password": hash_password("doctor123"), "full_name": "Dr. Kofi Mensah", "role": "doctor", "locale": "fr", "mfa_enabled": False, "mfa_secret": None, "is_active": True},
        {"_id": str(uuid.uuid4()), "email": "nurse@tropmed.local", "hashed_password": hash_password("nurse123"), "full_name": "Ama Adjei", "role": "nurse", "locale": "fr", "mfa_enabled": False, "mfa_secret": None, "is_active": True},
        {"_id": str(uuid.uuid4()), "email": "patient@tropmed.local", "hashed_password": hash_password("patient123"), "full_name": "Yao Koffi", "role": "patient", "locale": "fr", "mfa_enabled": False, "mfa_secret": None, "is_active": True},
    ]
    await db["users"].delete_many({})
    await db["users"].insert_many(users)

    # Patient
    patient_id = str(uuid.uuid4())
    await db["patients"].delete_many({})
    await db["patients"].insert_one({
        "_id": patient_id, "fhir_id": str(uuid.uuid4()),
        "given_name": "Yao", "family_name": "Koffi", "name_text": "Yao Koffi",
        "date_of_birth": "1985-03-15", "gender": "male", "phone": "+228 90 00 00 00",
        "locale": "fr", "status": "active",
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    })

    print(f"Seeded {len(users)} users, 1 patient")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
