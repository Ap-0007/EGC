import asyncio
import logging
from execution.agent_loader import AgentLoader
from execution.tool_runner import run_command

class AgentExecutor:
    def __init__(self, workspace_root: str):
        self.loader = AgentLoader(workspace_root)
        self.logger = logging.getLogger("AgentExecutor")

    async def execute_agent(self, agent_id: str, prompt: str, timeout: int = 60):
        agent_path = self.loader.load_agent(agent_id)
        if not agent_path:
            self.logger.error(f"Agent {agent_id} not found.")
            return {"status": "failed", "error": "Agent not found"}

        self.logger.info(f"Starting agent {agent_id} execution from {agent_path}")
        print(f"[TRACE] agent_executor.execute_agent | agent_id: {agent_id} | type: {type(agent_id)} | id: {id(agent_id)}")
        
        cmd = ["python3", "-c", f"print('Executing agent {agent_id} logic: {prompt}')"]
        
        return await run_command(cmd, timeout=timeout)
