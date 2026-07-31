import asyncio
import logging

logger = logging.getLogger(__name__)

class GPUMonitor:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self._running = False
        self._task = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("GPU Monitor started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("GPU Monitor stopped.")

    async def _monitor_loop(self):
        while self._running:
            try:
                import pynvml  # type: ignore
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                logger.info(f"GPU Stats | Util: {util.gpu}% | Mem: {mem.used/(1024**2):.0f}/{mem.total/(1024**2):.0f}MB | Temp: {temp}C")
                pynvml.nvmlShutdown()
            except ImportError:
                pass # pynvml not installed, suppress
            except Exception as e:
                logger.warning(f"Error during GPU monitoring: {e}")
            
            await asyncio.sleep(self.interval)
