"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Agent monitoring and metrics utilities."""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class AgentMetric:
    """Individual agent metric."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]


class AgentMonitor:
    """Monitor class for tracking agent metrics and performance."""

    def __init__(self):
        """Initialize the monitor."""
        self.metrics: List[AgentMetric] = []
        self.start_times: Dict[str, float] = {}

    def start_operation(self, operation_name: str):
        """Start timing an operation.

        Args:
            operation_name: Name of operation to time
        """
        self.start_times[operation_name] = time.time()

    def end_operation(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """End timing an operation and record metric.

        Args:
            operation_name: Name of operation that was timed
            labels: Optional labels to attach to metric
        """
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.record_metric(
                f"{operation_name}_duration_seconds",
                duration,
                labels or {}
            )
            del self.start_times[operation_name]

    def record_metric(self, name: str, value: float, labels: Dict[str, str]):
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            labels: Labels to attach to metric
        """
        self.metrics.append(AgentMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels
        ))

    def get_metrics(self) -> List[AgentMetric]:
        """Get all recorded metrics.

        Returns:
            List of recorded metrics
        """
        return self.metrics

    def clear_metrics(self):
        """Clear all recorded metrics."""
        self.metrics = []
