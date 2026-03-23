"""
Property tests for the MongoDB migration runner.

Feature: trop-med-fullstack-polish
Property 15: Migration runner writes correct records to _migrations
Property 16: Migration runner is idempotent
"""
import asyncio
from datetime import datetime
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st

from migrations.runner import run_migrations


def _make_migration(version: int, name: str, should_fail: bool = False) -> ModuleType:
    """Create a fake migration module."""
    mod = MagicMock(spec=["VERSION", "NAME", "up"])
    mod.VERSION = version
    mod.NAME = name
    if should_fail:
        mod.up = AsyncMock(side_effect=RuntimeError("migration failed"))
    else:
        mod.up = AsyncMock(return_value=None)
    return mod


def _make_db(applied_versions: set[int]) -> MagicMock:
    """Create a mock AsyncIOMotorDatabase."""
    db = MagicMock()

    # _migrations collection
    col = MagicMock()

    # find() returns an async iterator of {version: v} docs
    async def _aiter(self):
        for v in applied_versions:
            yield {"version": v}

    cursor = MagicMock()
    cursor.__aiter__ = _aiter
    col.find = MagicMock(return_value=cursor)
    col.insert_one = AsyncMock(return_value=None)
    col.count_documents = AsyncMock(return_value=len(applied_versions))

    db.__getitem__ = MagicMock(return_value=col)
    db._migrations_col = col  # convenience reference in tests
    return db


# ---------------------------------------------------------------------------
# Property 15: Migration runner writes correct records to _migrations
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    version=st.integers(min_value=1, max_value=1000),
    name=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd"),
            whitelist_characters="_",
        ),
    ),
)
def test_property_15_migration_writes_correct_record(version: int, name: str):
    """
    Feature: trop-med-fullstack-polish, Property 15: Migration runner writes correct records to _migrations
    For any migration that succeeds, _migrations should contain a document with correct version, name, applied_at.
    """
    mod = _make_migration(version, name)
    db = _make_db(applied_versions=set())

    with (
        patch("migrations.runner.pkgutil.iter_modules", return_value=[("", f"{version:04d}_{name}", False)]),
        patch("migrations.runner.importlib.import_module", return_value=mod),
    ):
        asyncio.run(run_migrations(db))

    col = db["_migrations"]
    col.insert_one.assert_called_once()
    call_args = col.insert_one.call_args[0][0]
    assert call_args["version"] == version
    assert call_args["name"] == name
    assert isinstance(call_args["applied_at"], datetime)
    assert call_args["applied_at"].tzinfo is not None  # timezone-aware


# ---------------------------------------------------------------------------
# Property 16: Migration runner is idempotent
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    all_versions=st.sets(st.integers(min_value=1, max_value=50), min_size=1, max_size=10),
    already_applied=st.sets(st.integers(min_value=1, max_value=50), min_size=0, max_size=10),
)
def test_property_16_migration_runner_is_idempotent(all_versions: set[int], already_applied: set[int]):
    """
    Feature: trop-med-fullstack-polish, Property 16: Migration runner is idempotent
    Running the runner should apply only migrations whose versions are absent from _migrations,
    leaving previously-applied records unchanged.
    """
    pending = all_versions - already_applied

    mods = [_make_migration(v, f"migration_{v:04d}") for v in all_versions]
    db = _make_db(applied_versions=already_applied)

    module_map = {f"{v:04d}_migration_{v:04d}": next(m for m in mods if v == m.VERSION) for v in all_versions}

    with (
        patch("migrations.runner.pkgutil.iter_modules", return_value=[("", name, False) for name in module_map]),
        patch("migrations.runner.importlib.import_module", side_effect=lambda n: module_map[n.split(".")[-1]]),
    ):
        asyncio.run(run_migrations(db))

    col = db["_migrations"]
    # insert_one should be called exactly once per pending migration
    assert col.insert_one.call_count == len(pending)

    # up() should only be called for pending migrations
    for mod in mods:
        if mod.VERSION in pending:
            mod.up.assert_called_once()
        else:
            mod.up.assert_not_called()
