@echo off
echo ===================================================
echo   FacultyIQ Enterprise AI Platform Launcher
echo ===================================================
echo.

:: --- PERMANENT FIX FOR GPU MUTUAL EXCLUSIVITY ---
:: Prevents ML frameworks from greedily allocating all VRAM on startup.
:: This allows both the Resume Agent and Video Agent to share the GPU.
set TF_FORCE_GPU_ALLOW_GROWTH=true
set FLAGS_allocator_strategy=auto_growth
set FLAGS_fraction_of_gpu_memory_to_use=0.1
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
set CUDA_MODULE_LOADING=LAZY
:: ------------------------------------------------

echo [1/8] Clearing previous instances on Ports 5229, 8000, 8005, 8010, 8015, and 8020...
powershell -Command "Get-NetTCPConnection -LocalPort 5229,8000,8005,8010,8015,8020 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [2/8] Starting AI Orchestrator (Port 8010)...
start "AI Orchestrator (Port 8010)" cmd /k "cd /d %~dp0ai-services\ai-orchestrator && ..\video-agent\venv\Scripts\python.exe -m uvicorn main:app --port 8010"

echo [3/8] Starting Resume Intelligence Engine (Port 8000)...
start "Resume Engine (Port 8000)" cmd /k "cd /d %~dp0ai-services\resume-parser-v2 && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

echo [4/8] Starting Video Evaluation Agent (Port 8005)...
start "Video Agent (Port 8005)" cmd /k "cd /d %~dp0ai-services\video-agent && venv\Scripts\python.exe -m uvicorn app.main:app --port 8005"

echo [5/8] Starting Frontend Web Application (Port 3002)...
start "Frontend UI (Port 3002)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [6/8] Starting Coding Intelligence Agent (Port 8015)...
start "Coding Agent (Port 8015)" cmd /k "cd /d %~dp0ai-services\coding-agent && venv\Scripts\python.exe -m uvicorn app.main:app --port 8015"

echo [7/8] Starting Backend API (Port 5229)...
start "Backend API (Port 5229)" cmd /k "cd /d %~dp0backend\src\FacultyIQ.Api && dotnet run"

echo [8/8] Starting Interaction Agent (Port 8020)...
start "Interaction Agent (Port 8020)" cmd /k "cd /d %~dp0ai-services\interaction-agent && venv\Scripts\python.exe -m uvicorn main:app --port 8020"

echo.
echo ===================================================
echo All services launched!
echo.
echo  - Frontend Web UI:          http://localhost:3002
echo  - Backend API:              http://localhost:5229
echo  - AI Orchestrator API:      http://localhost:8010
echo  - Resume Intelligence API:  http://localhost:8000
echo  - Video Agent API:          http://localhost:8005
echo  - Coding Agent API:         http://localhost:8015
echo  - Interaction Agent API:    http://localhost:8020
echo ===================================================
pause
