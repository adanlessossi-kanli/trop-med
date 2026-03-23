#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/docker"

echo "═══════════════════════════════════════"
echo "  Trop-Med — Starting all services"
echo "═══════════════════════════════════════"

cd "$COMPOSE_DIR"
docker compose up -d --build

echo ""
echo "⏳ Waiting for backend to be ready..."
MAX_RETRIES=30
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "⚠️  Backend did not become healthy in time — check logs with: docker compose -f $COMPOSE_DIR/docker-compose.yml logs backend"
        exit 1
    fi
    sleep 2
done

echo "🌱 Seeding database..."
docker compose exec -T backend python -m app.scripts.seed

echo ""
echo "═══════════════════════════════════════"
echo "  Trop-Med is running!"
echo ""
echo "  Frontend : http://localhost:3000"
echo "  Backend  : http://localhost:8000"
echo "  API docs : http://localhost:8000/docs"
echo "═══════════════════════════════════════"
