from typing import List, Dict, Any

class TaskPlanner:
    def plan(self, main_task: str) -> List[Dict[str, Any]]:
        # Simplified decomposition: split task into steps based on complexity
        # Real planner would use an LLM agent
        return [
            {"id": "step1", "agent": "python-expert", "prompt": f"Initialize: {main_task}"},
            {"id": "step2", "agent": "runtime-engineer", "prompt": f"Execute: {main_task}"}
        ]
