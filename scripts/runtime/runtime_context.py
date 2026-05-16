from typing import Dict, Any

class RuntimeContext:
    def __init__(self, session_id: str, workflow_id: str):
        self.session_id = session_id
        self.workflow_id = workflow_id
        self.global_state: Dict[str, Any] = {}
        self.agent_contexts: Dict[str, Dict[str, Any]] = {}

    def set_agent_context(self, agent_id: str, context: Dict[str, Any]):
        self.agent_contexts[agent_id] = context

    def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        return self.agent_contexts.get(agent_id, {})
