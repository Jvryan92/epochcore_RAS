"""Resilience strategy implementation for adaptive system behavior."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import time
import logging
import numpy as np
from collections import deque

from . import StrategyComponent
from ..core.config_validator import ConfigField
from ..core.error_handling import retry, safe_execute


@dataclass
class HealthMetrics:
    """Container for system health metrics."""

    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_rates: deque = field(default_factory=lambda: deque(maxlen=100))
    resource_usage: Dict[str, deque] = field(default_factory=dict)
    last_incident: Optional[float] = None
    recovery_times: List[float] = field(default_factory=list)


class ResilienceStrategy(StrategyComponent):
    """Implements system resilience capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize resilience strategy component.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__("resilience", config)
        self.health = HealthMetrics()
        self._recovery_handlers: Dict[str, Callable] = {}
        self._setup_validation()

    def _setup_validation(self):
        """Set up resilience-specific configuration validation."""
        self._validator.register_schema(
            self.name,
            super()._validator._schemas.get(self.name, [])
            + [
                ConfigField(
                    "error_threshold",
                    float,
                    False,
                    0.1,
                    lambda x: 0 <= x <= 1,
                    "Maximum acceptable error rate",
                ),
                ConfigField(
                    "response_threshold",
                    float,
                    False,
                    1.0,
                    lambda x: x > 0,
                    "Maximum acceptable response time in seconds",
                ),
                ConfigField(
                    "resource_thresholds",
                    dict,
                    False,
                    {},
                    None,
                    "Resource usage thresholds",
                ),
            ],
        )

    def _execute(self) -> Dict[str, Any]:
        """Execute resilience analysis.

        Returns:
            Dictionary containing analysis results
        """
        # Analyze system health
        health_status = self._analyze_health()

        # Check for incidents
        incidents = self._detect_incidents(health_status)

        # Apply recovery actions if needed
        if incidents:
            self._handle_incidents(incidents)

        # Update metrics
        self._update_metrics(health_status, incidents)

        return {
            "health_status": health_status,
            "incidents": incidents,
            "metrics": self._get_metrics_summary(),
        }

    def _analyze_health(self) -> Dict[str, Any]:
        """Analyze current system health.

        Returns:
            Dictionary containing health analysis
        """
        # Calculate response time stats
        response_times = list(self.health.response_times)
        avg_response = np.mean(response_times) if response_times else 0
        max_response = max(response_times) if response_times else 0

        # Calculate error rate
        error_rates = list(self.health.error_rates)
        current_error_rate = np.mean(error_rates) if error_rates else 0

        # Analyze resource usage
        resource_status = {}
        for resource, values in self.health.resource_usage.items():
            if values:
                resource_status[resource] = {
                    "current": values[-1],
                    "average": np.mean(values),
                    "peak": max(values),
                }

        return {
            "response_time": {
                "average": avg_response,
                "maximum": max_response,
                "samples": len(response_times),
            },
            "error_rate": {"current": current_error_rate, "samples": len(error_rates)},
            "resources": resource_status,
            "last_incident": self.health.last_incident,
            "avg_recovery_time": (
                np.mean(self.health.recovery_times)
                if self.health.recovery_times
                else None
            ),
        }

    def _detect_incidents(self, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect system incidents based on health status.

        Args:
            health_status: Current health status

        Returns:
            List of detected incidents
        """
        incidents = []
        thresholds = self.config.get("resource_thresholds", {})

        # Check response time
        if health_status["response_time"]["average"] > self.config.get(
            "response_threshold", 1.0
        ):
            incidents.append(
                {
                    "type": "high_latency",
                    "value": health_status["response_time"]["average"],
                    "threshold": self.config.get("response_threshold", 1.0),
                }
            )

        # Check error rate
        if health_status["error_rate"]["current"] > self.config.get(
            "error_threshold", 0.1
        ):
            incidents.append(
                {
                    "type": "high_error_rate",
                    "value": health_status["error_rate"]["current"],
                    "threshold": self.config.get("error_threshold", 0.1),
                }
            )

        # Check resource usage
        for resource, status in health_status["resources"].items():
            if resource in thresholds and status["current"] > thresholds[resource]:
                incidents.append(
                    {
                        "type": f"high_{resource}_usage",
                        "value": status["current"],
                        "threshold": thresholds[resource],
                    }
                )

        return incidents

    @retry(max_attempts=3)
    def _handle_incidents(self, incidents: List[Dict[str, Any]]):
        """Handle detected incidents.

        Args:
            incidents: List of incidents to handle
        """
        for incident in incidents:
            incident_type = incident["type"]
            if incident_type in self._recovery_handlers:
                try:
                    self._recovery_handlers[incident_type](incident)
                except Exception as e:
                    self.logger.error(
                        f"Error in recovery handler for {incident_type}: {e}"
                    )

    def _update_metrics(
        self, health_status: Dict[str, Any], incidents: List[Dict[str, Any]]
    ):
        """Update health metrics.

        Args:
            health_status: Current health status
            incidents: Detected incidents
        """
        # Record incident if any found
        if incidents:
            self.health.last_incident = time.time()

        # Update recovery times if we've recovered
        if (
            self.health.last_incident
            and not incidents
            and self.health.last_incident < time.time()
        ):
            recovery_time = time.time() - self.health.last_incident
            self.health.recovery_times.append(recovery_time)

            # Keep only last 100 recovery times
            if len(self.health.recovery_times) > 100:
                self.health.recovery_times = self.health.recovery_times[-100:]

    @safe_execute(logging.getLogger("strategy_ai_agent.strategy"), {})
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of health metrics.

        Returns:
            Dictionary containing metrics summary
        """
        return {
            "response_times": (
                {
                    "avg": np.mean(self.health.response_times),
                    "max": max(self.health.response_times),
                }
                if self.health.response_times
                else {}
            ),
            "error_rate": (
                np.mean(self.health.error_rates) if self.health.error_rates else 0
            ),
            "resources": {
                name: np.mean(values)
                for name, values in self.health.resource_usage.items()
                if values
            },
            "incidents": {
                "last": self.health.last_incident,
                "avg_recovery": (
                    np.mean(self.health.recovery_times)
                    if self.health.recovery_times
                    else None
                ),
            },
        }

    def register_recovery_handler(
        self, incident_type: str, handler: Callable[[Dict[str, Any]], None]
    ):
        """Register a recovery handler for an incident type.

        Args:
            incident_type: Type of incident to handle
            handler: Function to call for recovery
        """
        self._recovery_handlers[incident_type] = handler

    def record_response_time(self, response_time: float):
        """Record a response time measurement.

        Args:
            response_time: Response time in seconds
        """
        self.health.response_times.append(response_time)

    def record_error(self, error_rate: float):
        """Record an error rate measurement.

        Args:
            error_rate: Error rate value
        """
        self.health.error_rates.append(error_rate)

    def record_resource_usage(self, resource: str, value: float):
        """Record a resource usage measurement.

        Args:
            resource: Resource identifier
            value: Usage value
        """
        if resource not in self.health.resource_usage:
            self.health.resource_usage[resource] = deque(maxlen=100)
        self.health.resource_usage[resource].append(value)
