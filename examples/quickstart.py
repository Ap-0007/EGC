# Example Workflow
from orchestration.orchestrator import ExecutionOrchestrator
import asyncio
import os

async def main():
    orch = ExecutionOrchestrator(os.getcwd())
    print("Running Minimal Workflow...")
    # This validates that orchestrator and agent_loader are correctly importable
    print("Orchestrator loaded successfully.")

if __name__ == "__main__":
    asyncio.run(main())
