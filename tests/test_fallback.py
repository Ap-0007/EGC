import unittest
import asyncio
from scripts.orchestration.fallback import FALLBACK_MANAGER

class TestFallbackAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fm = FALLBACK_MANAGER(max_retries=1)

    async def test_retry_success(self):
        self.count = 0
        async def eventually_succeeds():
            self.count += 1
            if self.count < 2:
                raise Exception("Failure")
            return "Success"
        
        result = await self.fm.execute_with_retry_async(eventually_succeeds)
        self.assertEqual(result, "Success")
        self.assertEqual(self.count, 2)

    async def test_retry_failure(self):
        async def always_fails():
            raise ValueError("Permanent Error")
        
        with self.assertRaises(ValueError):
            await self.fm.execute_with_retry_async(always_fails)

    def test_alternative_agents(self):
        agents = ["a", "b", "c"]
        alt = self.fm.get_alternative_agents("a", agents)
        self.assertEqual(alt, ["b", "c"])

if __name__ == "__main__":
    unittest.main()
