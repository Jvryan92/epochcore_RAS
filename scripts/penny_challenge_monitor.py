#!/usr/bin/env python3
"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict

# Add main directory to Python path before imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Local imports after path setup
from penny_challenge import PennyChallenge  # noqa: E402
from scripts.ai_agent.core.agent_manager import AgentManager  # noqa: E402
from scripts.ai_agent.core.synchronizer import AgentSynchronizer  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PennyChallengeCoordinator:
    def __init__(self, agent_manager: AgentManager):
        self.penny_challenge = PennyChallenge()
        self.agent_manager = agent_manager
        self.synchronizer = AgentSynchronizer()

    async def monitor_transaction(self, transaction: Dict[str, Any]):
        """Monitor and analyze a single transaction using all agents."""
        # Create sync point for all agents to analyze the transaction
        sync_id = f"tx_{transaction['id']}"
        await self.synchronizer.create_sync_point(
            sync_id=sync_id,
            required_agents={'sentinel', 'optimizer', 'synth'}
        )

        # Security check by Sentinel
        sentinel = self.agent_manager.agents['sentinel']
        security_result = await sentinel.analyze_transaction(transaction)

        # Performance optimization by Optimizer
        optimizer = self.agent_manager.agents['optimizer']
        performance_result = await optimizer.optimize_transaction(transaction)

        # Market analysis by Synth
        synth = self.agent_manager.agents['synth']
        market_result = await synth.synthesize_market_impact(transaction)

        # Wait for all agents to complete
        await self.synchronizer.join_sync_point(sync_id, 'coordinator')

        # Contribute individual analyses to compound decision
        self.agent_manager.contribute_decision(
            'sentinel',
            'penny_challenge_health',
            security_result
        )

        self.agent_manager.contribute_decision(
            'optimizer',
            'penny_challenge_health',
            performance_result
        )

        self.agent_manager.contribute_decision(
            'synth',
            'penny_challenge_health',
            market_result
        )

        return self.agent_manager.get_compound_decision('penny_challenge_health')

    async def run_continuous_monitoring(self):
        """Run continuous monitoring of the penny challenge system."""
        logger.info("Starting continuous monitoring of Penny Challenge")

        while True:
            try:
                # Get latest transactions
                recent_txs = self.penny_challenge.transactions[-10:]

                for tx in recent_txs:
                    health_status = await self.monitor_transaction(tx)

                    # Log health status
                    logger.info(
                        f"Transaction {tx['id']} Health:\n"
                        f"Security: {health_status['security_score']}\n"
                        f"Performance: {health_status['performance_score']}\n"
                        f"Market Impact: {health_status['market_score']}\n"
                        f"Overall: {health_status['overall_score']}"
                    )

                # Wait before next check
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error before retry


def main():
    """Initialize and run the Penny Challenge monitoring system."""
    logger.info("Initializing Penny Challenge monitoring system")

    # Initialize agent manager with high-skill agents
    manager = AgentManager()

    # Initialize coordinator
    coordinator = PennyChallengeCoordinator(manager)

    # Run monitoring
    logger.info("Starting monitoring loop")
    asyncio.run(coordinator.run_continuous_monitoring())


if __name__ == "__main__":
    main()
