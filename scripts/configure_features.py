"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from ai_agent.core.agent_manager import AgentManager
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_compound_features(manager: AgentManager):
    # Revenue optimization compound features
    manager.register_compound_feature(
        'revenue_optimization',
        ['optimizer', 'synth']
    )

    # Security and compliance compound features
    manager.register_compound_feature(
        'compliance_monitoring',
        ['sentinel', 'optimizer']
    )

    # System health compound features
    manager.register_compound_feature(
        'system_resilience',
        ['sentinel', 'optimizer', 'synth']
    )

    # Market analysis compound features
    manager.register_compound_feature(
        'market_intelligence',
        ['synth', 'optimizer']
    )


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('compound_features')

    manager = AgentManager()

    # Register required agents first
    from ai_agent.agents.optimizer_agent import OptimizerAgent
    from ai_agent.agents.sentinel_agent import SentinelAgent
    from ai_agent.agents.synth_agent import SynthAgent

    agent_classes = {
        'sentinel': SentinelAgent,
        'optimizer': OptimizerAgent,
        'synth': SynthAgent
    }

    for agent_name, agent_class in agent_classes.items():
        if agent_name not in manager.agents:
            logger.info(f"Registering agent: {agent_name}")
            agent = agent_class(config={'type': agent_name})
            manager.register_agent(agent)

    setup_compound_features(manager)

    # Verify compound features
    logger.info("Registered compound features:")
    for feature_id in manager.compound_decisions.keys():
        logger.info(f"  - {feature_id}")


if __name__ == '__main__':
    main()
