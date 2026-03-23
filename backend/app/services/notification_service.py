import uuid
from datetime import datetime, timezone
from app.core.database import get_db

db = get_db


async def create_notification(user_id: str, title: str, body: str) -> dict:
    doc = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "body": body,
        "read": False,
        "created_at": datetime.now(timezone.utc),
    }
    await db()["notifications"].insert_one(doc)
    return doc


async def list_notifications(user_id: str) -> list:
    return await db()["notifications"].find({"user_id": user_id}).sort("created_at", -1).to_list(100)


async def mark_read(notification_id: str):
    await db()["notifications"].update_one({"_id": notification_id}, {"$set": {"read": True}})


async def mark_all_read(user_id: str):
    await db()["notifications"].update_many({"user_id": user_id, "read": False}, {"$set": {"read": True}})
