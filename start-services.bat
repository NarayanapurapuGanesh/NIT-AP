@echo off
echo ===================================================
echo   FacultyIQ Enterprise AI Platform Launcher
echo ===================================================
echo.
echo [1/5] Clearing previous instances on Ports 8000, 8005, and 8010...
powershell -Command "Get-NetTCPConnection -LocalPort 8000,8005,8010 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [2/5] Starting AI Orchestrator (Port 8010)...
start "AI Orchestrator (Port 8010)" cmd /k "cd /d %~dp0ai-services\ai-orchestrator && ..\video-agent\venv\Scripts\python.exe -m uvicorn main:app --port 8010"

echo [3/5] Starting Resume Intelligence Engine (Port 8000)...
start "Resume Engine (Port 8000)" cmd /k "cd /d %~dp0ai-services\resume-parser-v2 && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

echo [4/5] Starting Video Evaluation Agent (Port 8005)...
start "Video Agent (Port 8005)" cmd /k "cd /d %~dp0ai-services\video-agent && venv\Scripts\python.exe -m uvicorn app.main:app --port 8005"

echo [5/5] Starting Frontend Web Application (Port 3002)...
start "Frontend UI (Port 3002)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================================
echo All services launched!
echo.
echo  - Frontend Web UI:          http://localhost:3002
echo  - AI Orchestrator API:      http://localhost:8010
echo  - Resume Intelligence API:  http://localhost:8000
echo  - Video Agent API:          http://localhost:8005
echo ===================================================
pause
