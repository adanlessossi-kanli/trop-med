from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import close_db, get_db
from app.core.errors import AppError, app_error_handler, generic_error_handler
from app.api.routes import auth, patients, clinical, ai, files, surveillance, notifications, chat, patient_files, gdpr
from app.core.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure indexes
    db = get_db()
    await db["users"].create_index("email", unique=True)
    await db["patients"].create_index("fhir_id")
    await db["patients"].create_index("name_text")
    await db["encounters"].create_index("patient_id")
    await db["observations"].create_index([("patient_id", 1), ("code", 1)])
    await db["conditions"].create_index("patient_id")
    await db["medications"].create_index("patient_id")
    await db["conversations"].create_index("user_id")
    await db["files"].create_index("patient_id")
    await db["audit_logs"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["surveillance"].create_index([("region", 1), ("disease_code", 1), ("date", 1)])
    yield
    await close_db()


app = FastAPI(title="Trop-Med API", version="1.0.0", lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, generic_error_handler)

PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(patients.router, prefix=PREFIX)
app.include_router(patient_files.router, prefix=PREFIX)
app.include_router(clinical.router, prefix=PREFIX)
app.include_router(ai.router, prefix=PREFIX)
app.include_router(files.router, prefix=PREFIX)
app.include_router(surveillance.router, prefix=PREFIX)
app.include_router(notifications.router, prefix=PREFIX)
app.include_router(gdpr.router, prefix=PREFIX)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
