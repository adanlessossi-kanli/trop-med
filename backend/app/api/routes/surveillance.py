from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import RoleRequired
from app.models.schemas import SurveillanceReport
from app.services import surveillance_service

router = APIRouter(prefix="/surveillance", tags=["surveillance"])

allowed = RoleRequired("admin", "doctor", "researcher")


class ReportResponse(BaseModel):
    id: str
    region: str
    disease_code: str
    case_count: int
    date: str
    reporter_id: str = ""


@router.get(
    "/dashboard",
    summary="Get surveillance dashboard data",
    description=(
        "Return aggregated epidemiological data for the dashboard. "
        "Supports optional filtering by `region`, `disease_code`, `date_from`, and `date_to`. "
        "Restricted to admin, doctor, and researcher roles."
    ),
)
async def dashboard(
    user: Annotated[dict, Depends(allowed)],
    region: str = "",
    disease_code: str = "",
    date_from: str = "",
    date_to: str = "",
):
    return await surveillance_service.get_dashboard(region, disease_code, date_from, date_to)


@router.get(
    "/trends",
    summary="Get disease trend data",
    description=(
        "Return time-series trend data for a specific disease code. "
        "Supports `granularity` (day, week, month) and optional date range filtering. "
        "Restricted to admin, doctor, and researcher roles."
    ),
)
async def trends(
    disease_code: str,
    user: Annotated[dict, Depends(allowed)],
    granularity: str = "day",
    date_from: str = "",
    date_to: str = "",
):
    return await surveillance_service.get_trends(disease_code, granularity, date_from, date_to)


@router.get(
    "/alerts",
    summary="Get active surveillance alerts",
    description=(
        "Return a list of active epidemiological alerts (e.g. outbreak thresholds exceeded). "
        "Restricted to admin, doctor, and researcher roles."
    ),
)
async def alerts(user: Annotated[dict, Depends(allowed)]):
    return await surveillance_service.get_alerts()


@router.post(
    "/report",
    response_model=ReportResponse,
    summary="Submit a surveillance report",
    description=(
        "Submit a new disease case count report for a given region and disease code. "
        "Restricted to admin, doctor, and researcher roles."
    ),
)
async def report(data: SurveillanceReport, user: Annotated[dict, Depends(allowed)]):
    return await surveillance_service.submit_report(data)
