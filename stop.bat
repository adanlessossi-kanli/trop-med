@echo off
setlocal

set COMPOSE_DIR=%~dp0docker

echo ═══════════════════════════════════════
echo   Trop-Med — Stopping all services
echo ═══════════════════════════════════════

cd /d "%COMPOSE_DIR%"

if "%1"=="--clean" (
    echo Stopping and removing volumes...
    docker compose down -v
) else (
    docker compose down
)

echo.
echo All services stopped.
echo.
echo   Tip: use 'stop.bat --clean' to also remove database volumes.

endlocal
