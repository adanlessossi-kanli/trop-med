from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.security import RoleRequired
from app.models.schemas import SurveillanceReport
from app.services import surveillance_service

router = APIRouter(prefix="/surveillance", tags=["surveillance"])

allowed = RoleRequired("admin", "doctor", "researcher")


@router.get("/dashboard")
async def dashboard(
    user: Annotated[dict, Depends(allowed)],
    region: str = "",
    disease_code: str = "",
    date_from: str = "",
    date_to: str = "",
):
    return await surveillance_service.get_dashboard(region, disease_code, date_from, date_to)


@router.get("/trends")
async def trends(
    disease_code: str,
    user: Annotated[dict, Depends(allowed)],
    granularity: str = "day",
    date_from: str = "",
    date_to: str = "",
):
    return await surveillance_service.get_trends(disease_code, granularity, date_from, date_to)


@router.get("/alerts")
async def alerts(user: Annotated[dict, Depends(allowed)]):
    return await surveillance_service.get_alerts()


@router.post("/report")
async def report(data: SurveillanceReport, user: Annotated[dict, Depends(allowed)]):
    return await surveillance_service.submit_report(data)
