import logging
import time

logger = logging.getLogger(__name__)

class CUDADetector:
    def __init__(self):
        self.gpu_available = False
        self.device_name = "Unknown"
        self.total_vram_mb = 0
        self.cuda_version = "Unknown"
        
        self._detect()

    def _detect(self):
        try:
            # We use pynvml if available to get raw hardware stats
            import pynvml  # type: ignore
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self.device_name = pynvml.nvmlDeviceGetName(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self.total_vram_mb = mem_info.total / (1024 ** 2)
                self.gpu_available = True
                
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion()
                    self.cuda_version = f"Driver {driver_version}"
                except pynvml.NVMLError:
                    pass
            pynvml.nvmlShutdown()
        except ImportError:
            logger.warning("pynvml not installed, falling back to basic checks.")
        except Exception as e:
            logger.warning(f"pynvml init failed: {e}")
            
        if not self.gpu_available:
            try:
                import torch
                if torch.cuda.is_available():
                    self.gpu_available = True
                    self.device_name = torch.cuda.get_device_name(0)
                    self.total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
                    self.cuda_version = torch.version.cuda
            except ImportError:
                logger.warning("PyTorch not installed, cannot verify CUDA via torch.")

        if not self.gpu_available:
            logger.warning("No NVIDIA GPU detected or CUDA unavailable. Falling back to CPU mode.")
        else:
            logger.info(f"Detected GPU: {self.device_name}, VRAM: {self.total_vram_mb:.0f} MB")

    def is_available(self):
        return self.gpu_available
