from datetime import UTC, datetime

from fastapi import Request

from app.core.database import get_db


async def log_audit(
    user_id: str,
    role: str,
    action: str,
    resource_type: str,
    resource_id: str = "",
    request: Request | None = None,
    details: dict | None = None,
    phi_accessed: bool = False,
):
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user_id": user_id,
        "role": role,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": request.client.host if request and request.client else "",
        "user_agent": request.headers.get("user-agent", "") if request else "",
        "details": details or {},
        "phi_accessed": phi_accessed,
    }
    await get_db()["audit_logs"].insert_one(entry)
