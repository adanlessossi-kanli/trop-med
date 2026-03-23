from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(user: Annotated[dict, Depends(get_current_user)]):
    return await notification_service.list_notifications(user["sub"])


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str, user: Annotated[dict, Depends(get_current_user)]):
    await notification_service.mark_read(notification_id)
    return {"read": True}


@router.put("/read-all")
async def mark_all_read(user: Annotated[dict, Depends(get_current_user)]):
    await notification_service.mark_all_read(user["sub"])
    return {"read_all": True}
