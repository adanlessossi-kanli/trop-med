import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ai, auth, chat, clinical, files, gdpr, notifications, patient_files, patients, surveillance
from app.core.database import close_db, get_db
from app.core.errors import AppError, app_error_handler, generic_error_handler
from app.core.rate_limit import RateLimitMiddleware
from migrations.runner import run_migrations

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()

    # Check if this is a first-ever run (no migrations applied yet)
    first_run = await db["_migrations"].count_documents({}) == 0

    await run_migrations(db)

    if first_run:
        import subprocess
        import sys
        logger.info("First run detected — seeding database …")
        subprocess.run([sys.executable, "-m", "app.scripts.seed"], check=False)  # noqa: S603

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
