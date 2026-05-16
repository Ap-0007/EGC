from typing import Dict, Any
from execution.agent_registry import AgentRegistry

class IdentityResolver:
    def __init__(self, workspace_root: str):
        self.registry = AgentRegistry(workspace_root)
        self.cache = {}

    def resolve(self, semantic_name: str) -> Dict[str, Any]:
        if semantic_name in self.cache:
            return self.cache[semantic_name]
        
        path = self.registry.get_physical_path(semantic_name)
        
        if path:
            result = {
                "resolved_agent": path,
                "confidence": 0.95,
                "strategy": "direct_registry"
            }
        else:
            result = {
                "resolved_agent": None,
                "confidence": 0.0,
                "strategy": "failed"
            }
        
        self.cache[semantic_name] = result
        return result
