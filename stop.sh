#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/docker"

echo "═══════════════════════════════════════"
echo "  Trop-Med — Stopping all services"
echo "═══════════════════════════════════════"

cd "$COMPOSE_DIR"

if [ "$1" = "--clean" ]; then
    echo "🗑️  Stopping and removing volumes (MongoDB data, Redis, LocalStack)..."
    docker compose down -v
else
    docker compose down
fi

echo ""
echo "✅ All services stopped."
echo ""
echo "   Tip: use './stop.sh --clean' to also remove database volumes (MongoDB data will be lost)."
