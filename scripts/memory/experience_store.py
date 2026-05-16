from memory.persistent_memory import PersistentMemory
import hashlib

class ExperienceStore:
    def __init__(self, workspace_root: str):
        self.memory = PersistentMemory()

    def _hash_task(self, task: str) -> str:
        return hashlib.md5(task.encode()).hexdigest()

    async def record_success(self, task: str, agent_id: str, result: dict):
        await self.memory.store_experience(self._hash_task(task), agent_id, "success", result)

    async def recall(self, task: str):
        return await self.memory.recall_similar(self._hash_task(task))
