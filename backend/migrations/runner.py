"""MongoDB migration runner.

Usage:
    python -m backend.migrations.runner
"""
import asyncio
import importlib
import logging
import pkgutil
import traceback
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


def _get_migrations_pkg():
    """Return the migrations package, supporting both installed and direct-run contexts."""
    try:
        import backend.migrations as pkg
        return pkg
    except ModuleNotFoundError:
        import migrations as pkg  # type: ignore[import]
        return pkg


async def run_migrations(db: AsyncIOMotorDatabase) -> None:
    """Apply all pending migrations in ascending version order."""
    collection = db["_migrations"]

    # Collect applied versions
    applied = {doc["version"] async for doc in collection.find({}, {"version": 1})}

    migrations_pkg = _get_migrations_pkg()
    pkg_name = migrations_pkg.__name__

    # Discover migration modules (files named like 0001_*.py)
    modules = []
    for _finder, name, _ in pkgutil.iter_modules(migrations_pkg.__path__):
        if name == "runner":
            continue
        mod = importlib.import_module(f"{pkg_name}.{name}")
        modules.append(mod)

    # Sort by VERSION
    modules.sort(key=lambda m: m.VERSION)

    for mod in modules:
        if mod.VERSION in applied:
            logger.info("Migration %04d (%s) already applied — skipping.", mod.VERSION, mod.NAME)
            continue

        logger.info("Applying migration %04d: %s …", mod.VERSION, mod.NAME)
        try:
            await mod.up(db)
            await collection.insert_one(
                {
                    "version": mod.VERSION,
                    "name": mod.NAME,
                    "applied_at": datetime.now(UTC),
                }
            )
            logger.info("Migration %04d applied successfully.", mod.VERSION)
        except Exception:
            logger.error(
                "Migration %04d (%s) failed — halting.\n%s",
                mod.VERSION,
                mod.NAME,
                traceback.format_exc(),
            )
            raise


if __name__ == "__main__":
    import sys

    from app.core.database import get_db

    logging.basicConfig(level=logging.INFO)

    async def _main() -> None:
        db = get_db()
        await run_migrations(db)

    asyncio.run(_main())
    sys.exit(0)
