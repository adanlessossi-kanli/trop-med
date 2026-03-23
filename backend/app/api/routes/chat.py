import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.schemas import AIQueryRequest
from app.services import ai_service

router = APIRouter()


@router.websocket(
    "/ws/chat",
    name="chat_websocket",
)
async def chat_ws(ws: WebSocket, token: str = Query(..., description="JWT access token for authentication")):
    """
    WebSocket endpoint for real-time AI-assisted chat.

    Connect with a valid JWT access token as the `token` query parameter.
    Send JSON messages with the shape `{"type": "message", "content": "...", "locale": "fr"}`.
    Receive AI responses as `{"type": "ai_response", "content": "...", "confidence": 0.9, "sources": [...]}`.
    Typing indicators are sent as `{"type": "typing", "status": true}` before each AI response.
    The connection is closed with code 4001 if the token is invalid or expired.
    """
    settings = get_settings()
    try:
        user = decode_token(token, settings)
    except Exception:
        await ws.close(code=4001)
        return

    await ws.accept()
    conversation_id = str(uuid.uuid4())
    db = get_db()

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            if msg.get("type") == "typing":
                continue

            content = msg.get("content", "")
            locale = msg.get("locale", "fr")

            # Save user message
            await db["conversations"].update_one(
                {"_id": conversation_id},
                {"$push": {"messages": {"role": "user", "content": content, "timestamp": datetime.now(UTC)}},
                 "$setOnInsert": {"user_id": user["sub"], "created_at": datetime.now(UTC)}},
                upsert=True,
            )

            # Send typing indicator
            await ws.send_text(json.dumps({"type": "typing", "status": True}))

            # Get AI response
            ai_req = AIQueryRequest(question=content, context={"locale": locale, "patient_id": ""})
            result = await ai_service.query(ai_req)

            # Save assistant message
            await db["conversations"].update_one(
                {"_id": conversation_id},
                {"$push": {"messages": {
                    "role": "assistant", "content": result.answer,
                    "confidence": result.confidence,
                    "timestamp": datetime.now(UTC),
                }}},
            )

            await ws.send_text(json.dumps({
                "type": "ai_response",
                "content": result.answer,
                "confidence": result.confidence,
                "sources": result.sources,
            }))
    except WebSocketDisconnect:
        pass
