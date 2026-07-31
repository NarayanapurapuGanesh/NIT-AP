import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, limit_mb: float = 3500):
        self.limit_mb = limit_mb
        self.current_allocated_mb = 0.0

    def get_available_memory(self):
        try:
            import pynvml  # type: ignore
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            pynvml.nvmlShutdown()
            return mem_info.free / (1024 ** 2)
        except Exception as e:
            # Fallback if pynvml fails, return a safe guess based on tracked allocations
            return max(0, self.limit_mb - self.current_allocated_mb)

    def can_allocate(self, required_mb: float) -> bool:
        """Check if we can safely allocate required memory without exceeding limit."""
        if required_mb == 0:
            return True
            
        available = self.get_available_memory()
        if available >= required_mb:
            return True
            
        logger.warning(f"Memory check failed: Need {required_mb}MB but only {available}MB free.")
        return False
