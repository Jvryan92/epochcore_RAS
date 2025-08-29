"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from revenue_system import RevenueSystem
from ceiling_manager import CeilingManager
from ai_agent.core.agent_manager import AgentManager
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def monitor_system_metrics():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('system_monitor')

    # Initialize core systems
    agent_manager = AgentManager()
    ceiling_manager = CeilingManager()
    revenue_system = RevenueSystem()

    # Monitor agent performance impact
    agents = agent_manager.get_all_agents()
    for agent in agents:
        metrics = agent.get_metrics()
        logger.info(f"Agent {agent.name} performance metrics:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value}")

    # Monitor ceiling adjustments
    ceiling_configs = ceiling_manager.load_ceilings()
    logger.info("\nCeiling configurations:")
    for config_id, config in ceiling_configs.get("configurations", {}).items():
        logger.info(f"Config {config_id}:")
        logger.info(f"  Performance score: {config.get('performance_score', 'N/A')}")
        logger.info(f"  Dynamic adjustments: {config.get('dynamic_adjustments', {})}")

    # Monitor revenue impact
    revenue_metrics = revenue_system.get_current_metrics()
    logger.info("\nRevenue metrics:")
    logger.info(f"  Monthly recurring revenue: ${revenue_metrics.get('mrr', 0):,.2f}")
    logger.info(f"  Average revenue per user: ${revenue_metrics.get('arpu', 0):,.2f}")
    logger.info(
        f"  Conversion rate: {revenue_metrics.get('conversion_rate', 0)*100:.1f}%")

    # Generate system health report
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'agent_health': all(agent.is_healthy() for agent in agents),
        'system_performance': ceiling_configs.get('system_score', 1.0),
        'revenue_status': 'healthy' if revenue_metrics.get('mrr', 0) > 0 else 'needs_attention'
    }

    logger.info("\nSystem Health Report:")
    for key, value in report.items():
        logger.info(f"  {key}: {value}")


def main():
    monitor_system_metrics()


if __name__ == '__main__':
    main()
