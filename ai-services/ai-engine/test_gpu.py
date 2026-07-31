import asyncio
from core.gpu_manager import GPUManager
from config.config_loader import get_config
import logging

logging.basicConfig(level=logging.INFO)

async def test():
    config = get_config()
    manager = GPUManager(config.gpu_config)
    print(f"GPU Available: {manager.is_available}")
    print(f"Device: {manager.detector.device_name}")
    print(f"VRAM: {manager.detector.total_vram_mb}")

if __name__ == "__main__":
    asyncio.run(test())
