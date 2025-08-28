"""Asynchronous Agent Manager implementation."""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent
from .logger import setup_logging
from .agent_manager import AgentManager


class AsyncAgentManager(AgentManager):
    """Asynchronous manager class for coordinating multiple AI agents."""

    async def start_all_agents_async(self) -> Dict[str, Any]:
        """Start all registered agents asynchronously and return their results as a dict."""
        tasks = []
        for agent_name in self.agents:
            if hasattr(self.agents[agent_name], 'run_async'):
                tasks.append(self.agents[agent_name].run_async())
            else:
                # Create async wrapper for sync agents
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.agents[agent_name].run
                    )
                )
        
        results = {}
        completed_tasks = await asyncio.gather(*tasks)
        for agent_name, result in zip(self.agents.keys(), completed_tasks):
            results[agent_name] = result
            
        return results

    async def run_agent_async(self, agent_name: str) -> Dict[str, Any]:
        """Run a specific agent asynchronously.

        Args:
            agent_name: Name of agent to run

        Returns:
            Agent execution results
        """
        if agent_name not in self.agents:
            return {
                "status": "error",
                "error": f"Agent '{agent_name}' not found"
            }

        agent = self.agents[agent_name]
        if hasattr(agent, 'run_async'):
            return await agent.run_async()
        else:
            # Create async wrapper for sync agent
            return await asyncio.get_event_loop().run_in_executor(None, agent.run)
