"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from ai_agent.core.monitoring import AgentMetric, AgentMonitor
from ai_agent.core.agent_manager import AgentManager
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_monitoring():
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    logger = logging.getLogger('performance_monitor')

    # Initialize agent manager
    manager = AgentManager()

    # Core metrics to track
    core_metrics = {
        'success_rate': 'Success rate of operations',
        'latency': 'Operation latency in ms',
        'resource_usage': 'Resource utilization %'
    }

    return manager, core_metrics, logger


def main():
    manager, metrics_config, logger = setup_monitoring()

    # Get all active agents
    agents = manager.get_all_agents()

    for agent in agents:
        # Get agent metrics
        agent_metrics = agent.get_metrics()
        logger.info(f"Agent {agent.name} metrics:")

        # Log core metrics if available
        for metric_name, description in metrics_config.items():
            value = agent_metrics.get(metric_name, 'N/A')
            logger.info(f"  {metric_name} ({description}): {value}")

        # Log any additional metrics
        other_metrics = {
            k: v for k, v in agent_metrics.items()
            if k not in metrics_config
        }
        if other_metrics:
            logger.info("  Additional metrics:")
            for name, value in other_metrics.items():
                logger.info(f"    {name}: {value}")

        # Get compound features status
        try:
            features = manager.get_compound_features(agent.name)
            logger.info(f"Agent {agent.name} compound features:")
            for feature in features:
                logger.info(f"  {feature}: {features[feature]['status']}")
        except AttributeError:
            logger.info(f"No compound features found for {agent.name}")


if __name__ == '__main__':
    main()
