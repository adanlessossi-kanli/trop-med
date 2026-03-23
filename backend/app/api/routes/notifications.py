from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.schemas import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


class ReadResponse(BaseModel):
    read: bool


class ReadAllResponse(BaseModel):
    read_all: bool


@router.get(
    "",
    response_model=list[NotificationOut],
    summary="List notifications for the current user",
    description=(
        "Return all notifications addressed to the authenticated user, "
        "ordered by creation date descending. Includes both read and unread notifications."
    ),
)
async def list_notifications(user: Annotated[dict, Depends(get_current_user)]):
    return await notification_service.list_notifications(user["sub"])


@router.put(
    "/{notification_id}/read",
    response_model=ReadResponse,
    summary="Mark a notification as read",
    description="Mark a single notification as read by its unique identifier.",
)
async def mark_read(notification_id: str, user: Annotated[dict, Depends(get_current_user)]):
    await notification_service.mark_read(notification_id)
    return {"read": True}


@router.put(
    "/read-all",
    response_model=ReadAllResponse,
    summary="Mark all notifications as read",
    description="Mark every unread notification for the authenticated user as read in a single operation.",
)
async def mark_all_read(user: Annotated[dict, Depends(get_current_user)]):
    await notification_service.mark_all_read(user["sub"])
    return {"read_all": True}
