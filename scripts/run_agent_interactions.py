"""Integration script demonstrating high-skill agent interactions."""

import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json
import logging

from scripts.ai_agent.core.agent_manager import AgentManager
from scripts.ai_agent.agents.high_skill_agents import register_high_skill_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def run_agent_interaction_demo(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Run a demonstration of high-skill agent interactions.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Dictionary containing interaction results
    """
    # Initialize agent manager
    manager = AgentManager()

    # Load configuration
    config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)

    # Set default config values if not provided
    config.setdefault("mesh_secret", os.environ.get("MESH_SECRET", ""))
    config.setdefault("compliance_level", "high")
    config.setdefault("monitoring_interval", 300)
    config.setdefault("optimization_threshold", 0.75)
    config.setdefault("forecast_horizon", 30)

    # Register high-skill agents
    register_high_skill_agents(manager, config)
    logger.info("Registered high-skill agents")

    # Start all agents
    manager.start_all_agents()
    logger.info("Started all agents")

    try:
        # Simulate some interactions
        simulate_security_event(manager)
        time.sleep(1)  # Allow time for message processing

        simulate_performance_event(manager)
        time.sleep(1)

        simulate_market_event(manager)
        time.sleep(1)

        # Get compound feature results
        security_perf = manager.get_compound_decision("security_performance")
        market_security = manager.get_compound_decision("market_security")
        performance_market = manager.get_compound_decision("performance_market")
        system_status = manager.get_compound_decision("full_system_status")

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compound_decisions": {
                "security_performance": security_perf,
                "market_security": market_security,
                "performance_market": performance_market,
                "system_status": system_status,
            },
            "agent_status": manager.get_agent_status(),
        }

    finally:
        # Cleanup
        manager.stop_all_agents()
        logger.info("Stopped all agents")

    return results


def simulate_security_event(manager: AgentManager) -> None:
    """Simulate a security event for agent interaction."""
    sentinel = manager.get_agent("sentinel")
    if not sentinel:
        return

    # Simulate security alert
    alert_data = {
        "alert_type": "unauthorized_access",
        "severity": "high",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {"source": "external", "target": "api_endpoint", "attempts": 5},
    }

    sentinel.send_message(
        None, "security.alert", alert_data, priority="high"  # Broadcast
    )
    logger.info("Simulated security event")


def simulate_performance_event(manager: AgentManager) -> None:
    """Simulate a performance event for agent interaction."""
    optimizer = manager.get_agent("optimizer")
    if not optimizer:
        return

    # Simulate performance metrics
    metrics_data = {
        "latency": 450,  # Above threshold
        "cpu_usage": 85,  # Above threshold
        "memory_usage": 60,
        "request_rate": 1200,
        "error_rate": 0.02,
    }

    optimizer.send_message(
        None, "performance.metrics", metrics_data, priority="normal"  # Broadcast
    )
    logger.info("Simulated performance event")


def simulate_market_event(manager: AgentManager) -> None:
    """Simulate a market event for agent interaction."""
    synth = manager.get_agent("synth")
    if not synth:
        return

    # Simulate market metrics
    market_data = {
        "conversion_rate": 0.15,
        "customer_acquisition_cost": 45.00,
        "lifetime_value": 850.00,
        "churn_rate": 0.08,
        "market_share": 0.12,
    }

    synth.send_message(
        None, "market.metrics", market_data, priority="normal"  # Broadcast
    )
    logger.info("Simulated market event")


if __name__ == "__main__":
    # Run interaction demo
    results = run_agent_interaction_demo()

    # Pretty print results
    print("\nAgent Interaction Results:")
    print("-" * 50)
    print(json.dumps(results, indent=2))
    print("-" * 50)
