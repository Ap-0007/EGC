import asyncio
import json
import os
from workflows.task_planner import TaskPlanner
from workflows.workflow_state import WorkflowState
from execution.agent_executor import AgentExecutor
from runtime.runtime_context import RuntimeContext

class WorkflowEngine:
    def __init__(self, workspace_root: str):
        self.root = workspace_root
        self.planner = TaskPlanner()
        self.executor = AgentExecutor(workspace_root)
        self.workflow_dir = os.path.join(workspace_root, ".sessions/workflows")

    async def run(self, main_task: str, session_id: str):
        plan = self.planner.plan(main_task)
        state = WorkflowState()
        ctx = RuntimeContext(session_id, state.workflow_id)
        
        state.state = "running"
        for task in plan:
            res = await self.executor.execute_agent(task['agent'], task['prompt'])
            state.results[task['id']] = res
        
        state.state = "completed"
        self._persist(state)
        return state

    def _persist(self, state: WorkflowState):
        path = os.path.join(self.workflow_dir, f"{state.workflow_id}.json")
        serializable_results = {}
        for k, v in state.results.items():
            if hasattr(v, 'stdout'):
                serializable_results[k] = {
                    "stdout": v.stdout,
                    "stderr": v.stderr,
                    "returncode": v.returncode
                }
            else:
                serializable_results[k] = v
        
        data = {
            "workflow_id": state.workflow_id,
            "tasks": state.tasks,
            "results": serializable_results,
            "state": state.state
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
