import asyncio
import logging
import uuid
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.results: Dict[str, Any] = {}

    async def enqueue(self, task_type: str, payload: dict) -> str:
        task_id = str(uuid.uuid4())
        task_item = {
            "task_id": task_id,
            "type": task_type,
            "payload": payload,
            "status": "queued"
        }
        await self.queue.put(task_item)
        logger.info(f"Task {task_id} of type {task_type} enqueued.")
        return task_id

    async def dequeue(self) -> dict:
        return await self.queue.get()

    def mark_done(self):
        self.queue.task_done()

    def set_result(self, task_id: str, result: Any):
        self.results[task_id] = result
        
    def get_result(self, task_id: str):
        return self.results.get(task_id)
