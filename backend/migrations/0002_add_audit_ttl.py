"""Migration 0002: add TTL index on audit_logs.timestamp (90-day expiry)."""
from motor.motor_asyncio import AsyncIOMotorDatabase

VERSION: int = 2
NAME: str = "add_audit_ttl"


async def up(db: AsyncIOMotorDatabase) -> None:
    # 90 days in seconds = 7_776_000
    await db["audit_logs"].create_index("timestamp", expireAfterSeconds=7_776_000)
