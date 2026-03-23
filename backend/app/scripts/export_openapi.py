"""
Export the FastAPI OpenAPI schema to docs/api/openapi.json.

Usage (from the repository root):
    python backend/app/scripts/export_openapi.py
"""

import json
import os
import sys

# Ensure the repo root is on sys.path so that `backend` and `app` packages resolve.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

for path in (REPO_ROOT, BACKEND_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.main import app  # noqa: E402  (import after sys.path manipulation)

OUTPUT_PATH = os.path.join(REPO_ROOT, "docs", "api", "openapi.json")


def export() -> None:
    schema = app.openapi()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(schema, fh, indent=2, ensure_ascii=False)
    print(f"OpenAPI schema written to {OUTPUT_PATH}")


if __name__ == "__main__":
    export()
