import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflows.workflow_engine import WorkflowEngine

async def test_workflow():
    root = os.getcwd()
    engine = WorkflowEngine(root)
    
    print("--- Running Workflow Engine Test ---")
    state = await engine.run("Test workflow execution", "test-sess-1")
    
    assert state.state == "completed"
    assert len(state.results) == 2
    print(f"Workflow {state.workflow_id} completed successfully.")

if __name__ == "__main__":
    asyncio.run(test_workflow())
