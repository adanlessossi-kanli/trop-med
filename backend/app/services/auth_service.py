import uuid

import pyotp

from app.core.config import Settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.schemas import UserCreate, UserOut

db = get_db


async def register(data: UserCreate) -> UserOut:
    coll = db()["users"]
    if await coll.find_one({"email": data.email}):
        raise ValueError("Email already registered")
    doc = {
        "_id": str(uuid.uuid4()),
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "full_name": data.full_name,
        "role": data.role,
        "locale": data.locale,
        "mfa_enabled": False,
        "mfa_secret": None,
        "is_active": True,
    }
    await coll.insert_one(doc)
    return UserOut(
        id=doc["_id"], email=doc["email"],
        full_name=doc["full_name"], role=doc["role"], locale=doc["locale"],
    )


async def login(email: str, password: str, settings: Settings) -> dict:
    user = await db()["users"].find_one({"email": email, "is_active": True})
    if not user or not verify_password(password, user["hashed_password"]):
        raise ValueError("Invalid credentials")
    return {
        "access_token": create_access_token(user["_id"], user["role"], user["locale"], settings),
        "refresh_token": create_refresh_token(user["_id"], settings),
        "token_type": "bearer",
    }


async def refresh(refresh_token: str, settings: Settings) -> dict:
    payload = decode_token(refresh_token, settings)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")
    user = await db()["users"].find_one({"_id": payload["sub"], "is_active": True})
    if not user:
        raise ValueError("User not found")
    return {
        "access_token": create_access_token(user["_id"], user["role"], user["locale"], settings),
        "token_type": "bearer",
    }


async def setup_mfa(user_id: str) -> dict:
    secret = pyotp.random_base32()
    await db()["users"].update_one({"_id": user_id}, {"$set": {"mfa_secret": secret}})
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user_id, issuer_name="Trop-Med")
    return {"secret": secret, "uri": uri}


async def verify_mfa(user_id: str, code: str) -> bool:
    user = await db()["users"].find_one({"_id": user_id})
    if not user or not user.get("mfa_secret"):
        raise ValueError("MFA not configured")
    if pyotp.TOTP(user["mfa_secret"]).verify(code):
        await db()["users"].update_one({"_id": user_id}, {"$set": {"mfa_enabled": True}})
        return True
    return False
