"""High-skill agent initialization and registration module."""

import datetime as dt
from typing import Optional, Dict, Any
from pathlib import Path

from ..core.agent_manager import AgentManager
from ..agents.sentinel_agent import SentinelAgent
from ..agents.optimizer_agent import OptimizerAgent
from ..agents.synth_agent import SynthAgent


def register_high_skill_agents(
    manager: AgentManager, config: Optional[Dict[str, Any]] = None
) -> None:
    """Register high-skill agents with the manager.

    Args:
        manager: Agent manager instance
        config: Optional configuration dictionary
    """
    config = config or {}

    # Register Sentinel (Security & Compliance)
    sentinel_config = {
        "mesh_secret": config.get("mesh_secret", ""),
        "compliance_level": config.get("compliance_level", "high"),
        "audit_interval": config.get("audit_interval", 3600),
    }
    sentinel = SentinelAgent(config=sentinel_config)
    manager.register_agent(sentinel)

    # Register Optimizer (Performance & Resource)
    optimizer_config = {
        "monitoring_interval": config.get("monitoring_interval", 300),
        "optimization_threshold": config.get("optimization_threshold", 0.75),
        "target_slo": {
            "latency": config.get("latency_slo", 300),
            "cpu_usage": config.get("cpu_usage_slo", 80),
            "memory_usage": config.get("memory_usage_slo", 75),
        },
        "metrics_history": config.get("metrics_history", 1000),
    }
    optimizer = OptimizerAgent(config=optimizer_config)
    manager.register_agent(optimizer)

    # Register Synth (Market Synthesis)
    synth_config = {
        "forecast_horizon": config.get("forecast_horizon", 30),
        "confidence_threshold": config.get("confidence_threshold", 0.8),
        "update_interval": config.get("update_interval", 3600),
        "metrics_history": config.get("metrics_history", 1000),
    }
    synth = SynthAgent(config=synth_config)
    manager.register_agent(synth)

    # Register compound features that require multiple agents
    manager.register_compound_feature("security_performance", ["sentinel", "optimizer"])
    manager.register_compound_feature("market_security", ["sentinel", "synth"])
    manager.register_compound_feature("performance_market", ["optimizer", "synth"])
    manager.register_compound_feature(
        "full_system_status", ["sentinel", "optimizer", "synth"]
    )

    # Set up agent connections
    sentinel.connect_to_agent(optimizer)
    sentinel.connect_to_agent(synth)
    optimizer.connect_to_agent(sentinel)
    optimizer.connect_to_agent(synth)
    synth.connect_to_agent(sentinel)
    synth.connect_to_agent(optimizer)

    # Set up topic subscriptions for inter-agent communication
    sentinel.subscribe_to_topic("system.health")
    sentinel.subscribe_to_topic("security.alert")

    optimizer.subscribe_to_topic("security.alert")
    optimizer.subscribe_to_topic("market.metrics")

    synth.subscribe_to_topic("system.health")
    synth.subscribe_to_topic("performance.metrics")
