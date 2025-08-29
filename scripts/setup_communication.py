"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from ai_agent.core.synchronizer import AgentSynchronizer
from ai_agent.core.agent_manager import AgentManager
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_communication(manager: AgentManager):
    synchronizer = AgentSynchronizer()
    logger = logging.getLogger('agent_communication')

    # Configure message channels
    channels = {
        'system.health': ['sentinel', 'optimizer', 'synth'],
        'market.metrics': ['optimizer', 'synth'],
        'security.alerts': ['sentinel', 'optimizer'],
        'performance.data': ['optimizer', 'synth'],
        'audit.logs': ['sentinel'],
        'strategy.updates': ['synth', 'optimizer']
    }

    # Set up channels and subscriptions
    for channel, subscribers in channels.items():
        for agent_name in subscribers:
            agent = manager.get_agent(agent_name)
            if agent:
                agent.subscribe_to_topic(channel)
                logger.info(f"Agent {agent_name} subscribed to {channel}")

    # Set up sync points for coordinated operations
    sync_points = {
        'market_analysis': {'sentinel', 'synth'},
        'performance_check': {'optimizer', 'synth'},
        'security_audit': {'sentinel', 'optimizer'},
        'system_health': {'sentinel', 'optimizer', 'synth'}
    }

    # Register sync points
    for sync_id, required_agents in sync_points.items():
        synchronizer.create_sync_point(sync_id, required_agents)
        logger.info(f"Created sync point {sync_id} for agents: {required_agents}")


def main():
    logging.basicConfig(level=logging.INFO)
    manager = AgentManager()
    setup_communication(manager)


if __name__ == '__main__':
    main()
