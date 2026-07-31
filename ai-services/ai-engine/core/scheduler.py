import asyncio
import logging

logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self, max_gpu_jobs: int = 1):
        self.max_gpu_jobs = max_gpu_jobs
        self.current_gpu_jobs = 0
        self.lock = asyncio.Lock()
        self.gpu_semaphore = asyncio.Semaphore(max_gpu_jobs)

    async def acquire_gpu(self):
        """Wait until GPU is available for a heavy task."""
        await self.gpu_semaphore.acquire()
        async with self.lock:
            self.current_gpu_jobs += 1
            logger.info(f"Acquired GPU slot. Current jobs: {self.current_gpu_jobs}/{self.max_gpu_jobs}")

    async def release_gpu(self):
        """Release GPU after task completion."""
        async with self.lock:
            self.current_gpu_jobs = max(0, self.current_gpu_jobs - 1)
            logger.info(f"Released GPU slot. Current jobs: {self.current_gpu_jobs}/{self.max_gpu_jobs}")
        self.gpu_semaphore.release()
