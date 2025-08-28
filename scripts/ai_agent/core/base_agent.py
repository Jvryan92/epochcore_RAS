"""Base agent class for the StrategyDECK AI agent system."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class BaseAgent(ABC):
    """Abstract base class for all AI agents in the system."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base agent.

        Args:
            name: Agent name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"strategy_ai_agent.{name}")
        self._is_running = False

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Execute the agent's main functionality.

        Returns:
            Dictionary containing execution results and status
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the agent's configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def start(self) -> Dict[str, Any]:
        """Start the agent with error handling and logging.

        Returns:
            Dictionary containing execution results and status
        """
        try:
            self.logger.info(f"Starting agent: {self.name}")

            if not self.validate_config():
                raise ValueError(
                    f"Invalid configuration for agent {self.name}"
                )

            self._is_running = True
            result = self.run()

            self.logger.info(f"Agent {self.name} completed successfully")
            return {"status": "success", "agent": self.name, "result": result}

        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            return {"status": "error", "agent": self.name, "error": str(e)}
        finally:
            self._is_running = False

    def is_running(self) -> bool:
        """Check if the agent is currently running.

        Returns:
            True if agent is running, False otherwise
        """
        return self._is_running

    def get_project_root(self) -> Path:
        """Get the project root directory.

        Returns:
            Path to project root
        """
        return Path(__file__).resolve().parent.parent.parent.parent
