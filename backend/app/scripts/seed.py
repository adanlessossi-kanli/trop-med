"""Seed script: python -m app.scripts.seed"""

import asyncio
import uuid
from datetime import UTC, datetime

from app.core.database import close_db, get_db
from app.core.security import hash_password

USER_DEFAULTS = {"mfa_enabled": False, "mfa_secret": None, "is_active": True}


def _user(email: str, password: str, full_name: str, role: str) -> dict:
    return {
        "_id": str(uuid.uuid4()),
        "email": email,
        "hashed_password": hash_password(password),
        "full_name": full_name,
        "role": role,
        "locale": "fr",
        **USER_DEFAULTS,
    }


async def seed():
    db = get_db()

    users = [
        _user("admin@tropmed.local", "admin123", "Admin Trop-Med", "admin"),
        _user("doctor@tropmed.local", "doctor123", "Dr. Kofi Mensah", "doctor"),
        _user("nurse@tropmed.local", "nurse123", "Ama Adjei", "nurse"),
        _user("patient@tropmed.local", "patient123", "Yao Koffi", "patient"),
    ]
    await db["users"].delete_many({})
    await db["users"].insert_many(users)

    patient_id = str(uuid.uuid4())
    await db["patients"].delete_many({})
    await db["patients"].insert_one({
        "_id": patient_id,
        "fhir_id": str(uuid.uuid4()),
        "given_name": "Yao",
        "family_name": "Koffi",
        "name_text": "Yao Koffi",
        "date_of_birth": "1985-03-15",
        "gender": "male",
        "phone": "+228 90 00 00 00",
        "locale": "fr",
        "status": "active",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    print(f"Seeded {len(users)} users, 1 patient")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
