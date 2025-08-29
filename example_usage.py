"""Example usage of the Agent Evolution Marketplace"""

import asyncio
import uuid

from marketplace_launcher import AgentMarketplace


async def main():
    # Initialize marketplace
    marketplace = AgentMarketplace()

    # Create a new agent
    agent_id = str(uuid.uuid4())
    print(f"\nRegistering agent: {agent_id}")

    # Start with starter tier
    register_result = await marketplace.register_agent(agent_id, "starter")
    print("\nRegistration result:")
    print(f"Tier: {register_result['market']['subscription_tier']}")
    print(f"Systems: {list(register_result['systems'].keys())}")

    # Evolve agent a few times
    print("\nEvolving agent...")
    for i in range(3):
        evolution = await marketplace.evolve_agent(agent_id)
        print(f"\nEvolution {i+1} results:")
        print(f"Market update: {evolution['market']}")
        print(f"System updates: {evolution['systems']}")

    # Upgrade to pro tier
    print("\nUpgrading to pro tier...")
    upgrade = await marketplace.upgrade_tier(agent_id, "pro")
    print(f"Upgrade result: {upgrade}")

    # Show tier information
    print("\nTier Information:")
    for tier in ["starter", "pro", "enterprise", "unlimited"]:
        info = marketplace.get_tier_info(tier)
        print(f"\n{tier.title()} Tier:")
        print(f"Price: ${info['price']}/month")
        print(f"Systems: {info['systems']}")
        print(f"Features: {info['features']}")

    # Get agent information
    print("\nAgent Information:")
    agent_info = await marketplace.get_agent_info(agent_id)
    print(f"Subscription: {agent_info['market']['subscription_tier']}")
    print(f"Balance: ${agent_info['market']['balance']}")
    print(f"Active Systems: {list(agent_info['systems'].keys())}")


if __name__ == "__main__":
    asyncio.run(main())
