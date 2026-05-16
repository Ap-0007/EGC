import os
import logging
from execution.identity_resolver import IdentityResolver

class AgentLoader:
    def __init__(self, workspace_root: str):
        self.root = workspace_root
        self.resolver = IdentityResolver(workspace_root)
        self.cache = {}
        self.logger = logging.getLogger("AgentLoader")

    def load_agent(self, agent_id: str):
        if not isinstance(agent_id, str):
            self.logger.error(f"Invalid agent_id type: {type(agent_id)}")
            return None

        if agent_id in self.cache:
            return self.cache[agent_id]
        
        resolution = self.resolver.resolve(agent_id)
        if resolution["resolved_agent"]:
            path = os.path.join(self.root, resolution["resolved_agent"])
            self.cache[agent_id] = path
            return path
            
        return None
