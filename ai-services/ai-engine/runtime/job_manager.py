import asyncio
import logging
from core.gpu_manager import GPUManager
from ollama.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self, task_queue):
        self.queue = task_queue
        self.gpu_manager = GPUManager()
        self.ollama_client = OllamaClient()
        self._running = False
        self._worker_tasks = []

    async def start(self, num_workers=2):
        if self._running:
            return
        self._running = True
        for i in range(num_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self._worker_tasks.append(task)
        logger.info(f"JobManager started with {num_workers} workers.")

    async def stop(self):
        self._running = False
        for task in self._worker_tasks:
            task.cancel()
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
        logger.info("JobManager stopped.")

    async def _worker_loop(self, worker_id: int):
        logger.info(f"Worker {worker_id} started.")
        while self._running:
            try:
                task_item = await self.queue.dequeue()
                task_id = task_item["task_id"]
                task_type = task_item["type"]
                payload = task_item["payload"]
                
                logger.info(f"Worker {worker_id} processing task {task_id} ({task_type})")
                
                try:
                    result = await self._process_task(task_type, payload)
                    self.queue.set_result(task_id, {"status": "success", "data": result})
                except Exception as e:
                    logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                    self.queue.set_result(task_id, {"status": "error", "error": str(e)})
                finally:
                    self.queue.mark_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered an error: {e}")

    async def _process_task(self, task_type: str, payload: dict):
        # Determine if task requires heavy GPU
        heavy_gpu_tasks = ["whisper", "ocr", "ollama"]
        requires_gpu = task_type in heavy_gpu_tasks
        
        if requires_gpu:
            logger.info(f"Task {task_type} requires GPU. Waiting for slot...")
            await self.gpu_manager.acquire_gpu()
            
        try:
            if task_type == "ollama":
                prompt = payload.get("prompt", "")
                model = payload.get("model", "llama3")
                return await self.ollama_client.generate(model, prompt)
            elif task_type == "whisper":
                await asyncio.sleep(2) # Mock inference
                return {"text": "Simulated whisper output"}
            elif task_type == "ocr":
                await asyncio.sleep(1) # Mock inference
                return {"text": "Simulated OCR output"}
            elif task_type == "cpu_task":
                await asyncio.sleep(0.5) # Mock cpu work
                return {"status": "CPU work done"}
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        finally:
            if requires_gpu:
                await self.gpu_manager.release_gpu()
