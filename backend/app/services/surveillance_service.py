import uuid
from datetime import UTC, datetime

from app.core.database import get_db
from app.models.schemas import SurveillanceReport

db = get_db


async def get_dashboard(region: str = "", disease_code: str = "", date_from: str = "", date_to: str = "") -> dict:
    query: dict = {}
    if region:
        query["region"] = region
    if disease_code:
        query["disease_code"] = disease_code
    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to

    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": {"disease_code": "$disease_code", "region": "$region"},
            "total_cases": {"$sum": "$case_count"},
        }},
    ]
    results = await db()["surveillance"].aggregate(pipeline).to_list(500)
    return {"aggregations": results}


async def get_trends(disease_code: str, granularity: str = "day", date_from: str = "", date_to: str = "") -> list:
    query: dict = {"disease_code": disease_code}
    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to
    return await db()["surveillance"].find(query).sort("date", 1).to_list(1000)


async def get_alerts() -> list:
    # Simple threshold-based alert: diseases with >50 cases in a single report
    return await db()["surveillance"].find({"case_count": {"$gt": 50}}).sort("date", -1).to_list(50)


async def submit_report(data: SurveillanceReport) -> dict:
    doc = {"_id": str(uuid.uuid4()), **data.model_dump(), "created_at": datetime.now(UTC)}
    await db()["surveillance"].insert_one(doc)
    return doc
