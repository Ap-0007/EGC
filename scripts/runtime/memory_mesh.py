import asyncio
import time
from typing import Dict, Any, Optional

class MemoryMesh:
    def __init__(self, ttl: int = 300):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
        self.lock = asyncio.Lock()

    async def put(self, key: str, value: Any, workflow_id: str):
        async with self.lock:
            self.data[key] = {
                "value": value,
                "workflow": workflow_id,
                "expires": time.time() + self.ttl
            }

    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            item = self.data.get(key)
            if item and time.time() < item["expires"]:
                return item["value"]
            if item:
                del self.data[key]
            return None
