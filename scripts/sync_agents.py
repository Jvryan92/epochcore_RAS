"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

from ai_agent.core.agent_manager import AgentManager
from ai_agent.agents.high_skill_agents import register_high_skill_agents
import os
import sys

# Add scripts directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
sys.path.append(scripts_dir)


def main():
    # Initialize agent manager
    manager = AgentManager()

    # Configure high-skill agents
    config = {
        'mesh_secret': os.getenv('MESH_SECRET', 'epoch5_mesh'),
        'compliance_level': 'high',
        'monitoring_interval': 300,
        'optimization_threshold': 0.75,
        'forecast_horizon': 30,
        'confidence_threshold': 0.8,
        'update_interval': 3600,
        'metrics_history': 1000,
        'target_slo': {
            'latency': 300,
            'cpu_usage': 80,
            'memory_usage': 75
        }
    }

    # Register and initialize agents
    register_high_skill_agents(manager, config)

    # Start all agents
    results = manager.start_all_agents()

    # Print initialization status
    for agent_name, status in results.items():
        print(f"{agent_name}: {status['status']}")


if __name__ == "__main__":
    main()
