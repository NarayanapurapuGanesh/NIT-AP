import logging
from typing import Optional
from .cuda_detector import CUDADetector
from .memory_manager import MemoryManager
from .scheduler import JobScheduler

logger = logging.getLogger(__name__)

class GPUManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GPUManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[dict] = None):
        if self._initialized:
            return
            
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        
        # Core components
        self.detector = CUDADetector()
        limit_mb = self.config.get("memory_limit_mb", 3500)
        self.memory_manager = MemoryManager(limit_mb=limit_mb)
        
        max_jobs = self.config.get("max_parallel_gpu_jobs", 1)
        self.scheduler = JobScheduler(max_gpu_jobs=max_jobs)
        
        self.performance_mode = self.config.get("performance_mode", False)
        
        self._initialized = True
        logger.info(f"GPU Manager initialized. Max concurrent heavy tasks: {max_jobs}")

    @property
    def is_available(self):
        return self.enabled and self.detector.is_available()

    async def acquire_gpu(self):
        """Wrapper for acquiring GPU resource."""
        if not self.is_available:
            return # Fallback to CPU, no wait required
        await self.scheduler.acquire_gpu()

    async def release_gpu(self):
        """Wrapper for releasing GPU resource."""
        if not self.is_available:
            return
        await self.scheduler.release_gpu()
