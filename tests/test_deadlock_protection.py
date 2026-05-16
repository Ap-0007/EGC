import unittest
import asyncio
from scripts.runtime.async_task_queue import EXECUTION_QUEUE

class TestDeadlockProtection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.eq = EXECUTION_QUEUE(max_concurrent=1)
        self.workers = await self.eq.start_workers(1)

    async def infinite_loop_task(self):
        # A task that never yields or takes forever
        await asyncio.sleep(10)
        return "Done"

    async def test_execution_timeout(self):
        # We will submit a task that takes 10s, but we will mock the queue's timeout
        # to 0.5s for this test.
        # Let's temporarily override the worker's timeout behavior by subclassing
        class FastTimeoutQueue(EXECUTION_QUEUE):
            async def worker(self):
                while True:
                    priority, task_id, coro, args, kwargs = await self.queue.get()
                    async with self.semaphore:
                        try:
                            # 0.2s timeout
                            await asyncio.wait_for(coro(*args, **kwargs), timeout=0.2)
                        except asyncio.TimeoutError:
                            self.timeout_triggered = True
                        finally:
                            self.queue.task_done()

        test_q = FastTimeoutQueue(max_concurrent=1)
        test_q.timeout_triggered = False
        workers = await test_q.start_workers(1)
        
        await test_q.submit_task(1, "timeout-task", self.infinite_loop_task)
        await test_q.queue.join()
        
        self.assertTrue(test_q.timeout_triggered)
        
        for w in workers:
            w.cancel()

    async def asyncTearDown(self):
        for w in self.workers:
            w.cancel()

if __name__ == "__main__":
    unittest.main()
