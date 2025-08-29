"""Strategy module integration."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
import logging

from ..core.base_agent import BaseAgent
from ..core.metrics import AgentMetrics
from ..core.error_handling import retry, log_errors, safe_execute
from ..core.config_validator import ConfigValidator, AGENT_BASE_SCHEMA


class StrategyComponent:
    """Base class for all strategy components."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize strategy component.

        Args:
            name: Component name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"strategy_ai_agent.strategy.{name}")
        self.metrics = AgentMetrics(f"strategy_{name}")
        self._validator = ConfigValidator()
        self._setup_validation()

    def _setup_validation(self):
        """Set up configuration validation schema."""
        self._validator.register_schema(
            self.name,
            AGENT_BASE_SCHEMA
            + [
                # Add component-specific schema fields here
            ],
        )

    @log_errors(logging.getLogger("strategy_ai_agent.strategy"))
    def validate(self) -> tuple[bool, List[str]]:
        """Validate component configuration.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        return self._validator.validate(self.name, self.config)

    @retry(max_attempts=3)
    def execute(self) -> Dict[str, Any]:
        """Execute the strategy component's main functionality.

        Returns:
            Dictionary containing execution results
        """
        self.metrics.start_run()
        try:
            result = self._execute()
            self.metrics.end_run(success=True)
            return {
                "status": "success",
                "component": self.name,
                "result": result,
                "metrics": self.metrics.get_metrics_summary(),
            }
        except Exception as e:
            self.metrics.end_run(success=False, error=e)
            raise

    def _execute(self) -> Dict[str, Any]:
        """Internal execution method to be implemented by subclasses.

        Returns:
            Dictionary containing execution results
        """
        raise NotImplementedError

    @safe_execute(logging.getLogger("strategy_ai_agent.strategy"), {})
    def get_status(self) -> Dict[str, Any]:
        """Get component status information.

        Returns:
            Dictionary containing component status
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "metrics": self.metrics.get_metrics_summary(),
            "config": self.config,
        }
