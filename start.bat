@echo off
setlocal

set COMPOSE_DIR=%~dp0docker

echo ═══════════════════════════════════════
echo   Trop-Med — Starting all services
echo ═══════════════════════════════════════

cd /d "%COMPOSE_DIR%"
docker compose up -d --build

echo.
echo Waiting for backend to be ready...
set MAX_RETRIES=30
set COUNT=0

:healthcheck
set /a COUNT+=1
curl -sf http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo Backend is healthy
    goto seed
)
if %COUNT% geq %MAX_RETRIES% (
    echo WARNING: Backend did not become healthy in time.
    echo Check logs with: docker compose -f "%COMPOSE_DIR%\docker-compose.yml" logs backend
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto healthcheck

:seed
echo Seeding database...
docker compose exec -T backend python -m app.scripts.seed

echo.
echo ═══════════════════════════════════════
echo   Trop-Med is running!
echo.
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo   API docs : http://localhost:8000/docs
echo ═══════════════════════════════════════

endlocal
