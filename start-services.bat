@echo off
echo ===================================================
echo   FacultyIQ Enterprise AI Platform Launcher
echo ===================================================
echo.
echo [1/4] Clearing previous instances on Ports 8000 and 8005...
powershell -Command "Get-NetTCPConnection -LocalPort 8000,8005 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [2/4] Starting Resume Intelligence Engine (Port 8000)...
start "Resume Engine (Port 8000)" cmd /k "cd /d %~dp0ai-services\resume-parser-v2 && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

echo [3/4] Starting Video Evaluation Agent (Port 8005)...
start "Video Agent (Port 8005)" cmd /k "cd /d %~dp0ai-services\video-agent && venv\Scripts\python.exe -m uvicorn app.main:app --port 8005"

echo [4/4] Starting Frontend Web Application (Port 3002)...
start "Frontend UI (Port 3002)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================================
echo All services launched!
echo.
echo  - Frontend Web UI:          http://localhost:3002
echo  - Resume Intelligence API:  http://localhost:8000
echo  - Video Agent API:          http://localhost:8005
echo ===================================================
pause
