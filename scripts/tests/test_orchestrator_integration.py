import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestration.orchestrator import ExecutionOrchestrator

async def test_integration():
    root = os.getcwd()
    orch = ExecutionOrchestrator(root)
    
    print("--- Running Orchestrator Integration Tests ---")
    
    # 1. Valid Execution
    res1 = await orch.execute_task("Test command", ["python3", "--version"], os.path.join(root, "scripts"), "sess1")
    print(f"Test 1 (Valid): {'PASS' if res1['status'] == 'completed' else 'FAIL'}")
    
    # 2. Blocked Execution
    res2 = await orch.execute_task("Blocked cmd", ["rm", "-rf", "/"], os.path.join(root, "scripts"), "sess1")
    print(f"Test 2 (Blocked): {'PASS' if res2['status'] == 'blocked' else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(test_integration())
