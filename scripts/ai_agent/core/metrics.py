"""Metrics and monitoring system for AI agents."""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import psutil
import prometheus_client as prom


@dataclass
class AgentMetrics:
    """Container for agent performance metrics."""

    name: str
    start_time: Optional[float] = None
    runs_total: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    last_run_duration: Optional[float] = None
    performance_metrics: List[Dict[str, Any]] = field(default_factory=list)
    last_error: Optional[tuple[str, str]] = None

    # Prometheus metrics
    success_counter = prom.Counter(
        "agent_success_total", "Total successful agent runs", ["agent_name"]
    )
    error_counter = prom.Counter(
        "agent_errors_total", "Total agent errors", ["agent_name"]
    )
    duration_histogram = prom.Histogram(
        "agent_duration_seconds", "Agent execution duration", ["agent_name"]
    )
    memory_gauge = prom.Gauge(
        "agent_memory_bytes", "Agent memory usage in bytes", ["agent_name", "type"]
    )

    def start_run(self) -> None:
        """Record the start of an agent run."""
        self.start_time = time.time()

    def end_run(self, success: bool, error: Optional[Exception] = None) -> None:
        """Record the end of an agent run with results.

        Args:
            success: Whether the run was successful
            error: Optional exception if the run failed
        """
        if self.start_time is None:
            return

        duration = time.time() - self.start_time
        self.runs_total += 1
        self.last_run_duration = duration
        self.total_duration += duration

        if success:
            self.success_count += 1
            self.success_counter.labels(agent_name=self.name).inc()
        else:
            self.error_count += 1
            if error:
                self.last_error = (type(error).__name__, str(error))
            self.error_counter.labels(agent_name=self.name).inc()

        self.duration_histogram.labels(agent_name=self.name).observe(duration)
        self._update_memory_metrics()
        self._record_performance_metrics(duration, success)

    def _update_memory_metrics(self) -> None:
        """Update memory usage metrics."""
        process = psutil.Process()
        memory = process.memory_info()

        self.memory_gauge.labels(agent_name=self.name, type="rss").set(memory.rss)

        self.memory_gauge.labels(agent_name=self.name, type="vms").set(memory.vms)

    def _record_performance_metrics(self, duration: float, success: bool) -> None:
        """Record detailed performance metrics.

        Args:
            duration: Run duration in seconds
            success: Whether the run was successful
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "success": success,
            "memory_usage": self._get_memory_usage(),
        }
        self.performance_metrics.append(metrics)

        # Keep only last 100 metrics
        if len(self.performance_metrics) > 100:
            self.performance_metrics = self.performance_metrics[-100:]

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics.

        Returns:
            Dictionary with memory usage metrics in MB
        """
        process = psutil.Process()
        memory = process.memory_info()
        return {"rss": memory.rss / 1024 / 1024, "vms": memory.vms / 1024 / 1024}

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage.

        Returns:
            Success rate as a percentage
        """
        if self.runs_total == 0:
            return 0.0
        return (self.success_count / self.runs_total) * 100

    def get_average_duration(self) -> float:
        """Calculate average run duration.

        Returns:
            Average duration in seconds
        """
        if self.runs_total == 0:
            return 0.0
        return self.total_duration / self.runs_total

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics.

        Returns:
            Dictionary containing all relevant metrics
        """
        return {
            "name": self.name,
            "total_runs": self.runs_total,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.get_success_rate(),
            "avg_duration": self.get_average_duration(),
            "last_run_duration": self.last_run_duration,
            "last_error": self.last_error,
            "memory_usage": self._get_memory_usage(),
            "recent_performance": self.performance_metrics[-5:],  # Last 5 runs
        }
