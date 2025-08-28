"""StrategyDECK AI Agent System.

A dedicated AI agent system for automating strategic tasks and processes
within the StrategyDECK project.
"""

__version__ = "1.1.0"
__author__ = "StrategyDECK Team"

from .core.agent_manager import AgentManager
from .core.async_agent_manager import AsyncAgentManager
from .core.base_agent import BaseAgent
from .core.async_base_agent import AsyncBaseAgent
from .core.logger import get_logger, setup_logging
from .core.monitoring import AgentMonitor, AgentMetric
from .core.scheduler import AgentScheduler
from .core.error_handling import RetryableError, AgentError, with_retry, safe_operation

from .agents.strategy_agent import StrategyAgent, TaskType
from .agents.asset_manager import AssetManagerAgent
from .agents.project_monitor import ProjectMonitorAgent
from .agents.workflow_optimizer import WorkflowOptimizerAgent

__all__ = [
    # Core components
    "AgentManager",
    "AsyncAgentManager",
    "BaseAgent", 
    "AsyncBaseAgent",
    "get_logger",
    "setup_logging",
    
    # Monitoring & scheduling
    "AgentMonitor",
    "AgentMetric",
    "AgentScheduler",
    
    # Error handling
    "RetryableError",
    "AgentError",
    "with_retry",
    "safe_operation",
    
    # Agent implementations
    "StrategyAgent",
    "TaskType",
    "AssetManagerAgent",
    "ProjectMonitorAgent",
    "WorkflowOptimizerAgent",
]
