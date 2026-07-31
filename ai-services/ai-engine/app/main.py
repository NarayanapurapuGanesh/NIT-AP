import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from config.config_loader import get_config
from core.gpu_manager import GPUManager
from monitoring.gpu_monitor import GPUMonitor
from runtime.task_queue import TaskQueue
from runtime.job_manager import JobManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FacultyIQ AI Engine", description="GPU Orchestrator for AI Services")

# Globals
config = get_config()
gpu_manager = None
gpu_monitor = None
task_queue = None
job_manager = None

@app.on_event("startup")
async def startup_event():
    global gpu_manager, gpu_monitor, task_queue, job_manager
    
    logger.info("Starting FacultyIQ AI Engine (GPU Orchestrator)...")
    
    # Initialize Core
    gpu_manager = GPUManager(config.gpu_config)
    
    # Initialize Monitor
    gpu_monitor = GPUMonitor()
    await gpu_monitor.start()
    
    # Initialize Queue and JobManager
    task_queue = TaskQueue()
    job_manager = JobManager(task_queue)
    
    # Start worker threads based on concurrency limit in config (usually 1 heavy + some light)
    # We'll use 4 workers, but the GPU scheduler limits heavy ones to 1
    await job_manager.start(num_workers=4)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FacultyIQ AI Engine...")
    if job_manager:
        await job_manager.stop()
    if gpu_monitor:
        await gpu_monitor.stop()

class TaskRequest(BaseModel):
    task_type: str
    payload: dict

@app.post("/api/v1/tasks")
async def enqueue_task(request: TaskRequest):
    if not task_queue:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    task_id = await task_queue.enqueue(request.task_type, request.payload)
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    if not task_queue:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    result = task_queue.get_result(task_id)
    if result is None:
        return {"task_id": task_id, "status": "queued_or_running"}
    
    return {"task_id": task_id, "result": result}

@app.get("/api/v1/status")
async def get_system_status():
    if not gpu_manager:
        raise HTTPException(status_code=503, detail="Service unavailable")
        
    return {
        "gpu_available": gpu_manager.is_available,
        "device_name": gpu_manager.detector.device_name,
        "total_vram_mb": gpu_manager.detector.total_vram_mb,
        "current_heavy_jobs": gpu_manager.scheduler.current_gpu_jobs,
        "max_heavy_jobs": gpu_manager.scheduler.max_gpu_jobs,
        "performance_mode": config.performance_config.get("mode")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
