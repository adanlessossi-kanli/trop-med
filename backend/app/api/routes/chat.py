import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.config import get_settings
from app.core.security import decode_token
from app.core.database import get_db
from app.services import ai_service
from app.models.schemas import AIQueryRequest

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket, token: str = Query(...)):
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
                {"$push": {"messages": {"role": "user", "content": content, "timestamp": datetime.now(timezone.utc)}},
                 "$setOnInsert": {"user_id": user["sub"], "created_at": datetime.now(timezone.utc)}},
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
                {"$push": {"messages": {"role": "assistant", "content": result.answer, "confidence": result.confidence, "timestamp": datetime.now(timezone.utc)}}},
            )

            await ws.send_text(json.dumps({
                "type": "ai_response",
                "content": result.answer,
                "confidence": result.confidence,
                "sources": result.sources,
            }))
    except WebSocketDisconnect:
        pass
