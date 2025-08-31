"""Agent manager for coordinating and running multiple AI agents."""

from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent
from .logger import setup_logging


class AgentManager:
    """Manager class for coordinating multiple AI agents."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.config = self._load_config(config_path)

        # Setup logging
        log_file = None
        if self.config.get("logging", {}).get("file"):
            log_file = Path(self.config["logging"]["file"])

        self.logger = setup_logging(
            log_level=self.config.get("logging", {}).get("level", "INFO"),
            log_file=log_file,
            console_output=self.config.get("logging", {}).get("console", True),
        )

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if config_path and config_path.exists():
            import json

            with open(config_path, "r") as f:
                return json.load(f)

        # Default configuration
        return {
            "logging": {"level": "INFO", "console": True, "file": None},
            "agents": {},
        }

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the manager.

        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def run_agent(self, agent_name: str) -> Dict[str, Any]:
        """Run a specific agent by name.

        Args:
            agent_name: Name of the agent to run

        Returns:
            Dictionary containing execution results
        """
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found"
            self.logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        self.logger.info(f"Running agent: {agent_name}")
        return self.agents[agent_name].start()

    def run_all_agents(self) -> List[Dict[str, Any]]:
        """Run all registered agents.

        Returns:
            List of execution results for all agents
        """
        results = []
        self.logger.info("Running all agents")

        for agent_name in self.agents:
            result = self.run_agent(agent_name)
            results.append(result)

        return results

    def list_agents(self) -> List[str]:
        """Get list of registered agent names.

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def get_agent_status(self) -> Dict[str, bool]:
        """Get running status of all agents.

        Returns:
            Dictionary mapping agent names to their running status
        """
        return {
            name: agent.is_running() for name, agent in self.agents.items()
        }
