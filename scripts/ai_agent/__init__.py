"""StrategyDECK AI Agent System.

A dedicated AI agent system for automating strategic tasks and processes
within the StrategyDECK project.
"""

__version__ = "1.0.0"
__author__ = "StrategyDECK Team"

from .core.agent_manager import AgentManager
from .core.base_agent import BaseAgent

__all__ = ["AgentManager", "BaseAgent"]
