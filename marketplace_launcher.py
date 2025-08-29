"""Agent Evolution Marketplace Launcher"""

import asyncio
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional

from arcade_system import AgentArcadeSystem
from battle_system import BattleLeagueSystem
from champion_system import ChampionCreatorSystem
from dynasty_system import DynastySystem
from epoch_system import EpochSystem
from pricing_system import MarketplaceSystem


class AgentMarketplace:
    """Marketplace launcher integrating all systems with pricing tiers"""

    def __init__(self, root_dir: str = "data/marketplace"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

        # Initialize core systems
        self.market = MarketplaceSystem(root_dir)
        self.arcade = AgentArcadeSystem(root_dir)
        self.battle = BattleLeagueSystem(root_dir)
        self.champion = ChampionCreatorSystem(root_dir)
        self.dynasty = DynastySystem(root_dir)
        self.epoch = EpochSystem(root_dir)

        # System access by tier
        self.tier_systems = {
            "starter": ["arcade"],
            "pro": ["arcade", "battle", "champion"],
            "enterprise": ["arcade", "battle", "champion", "dynasty"],
            "unlimited": ["arcade", "battle", "champion", "dynasty", "epoch"]
        }

    async def register_agent(
        self,
        agent_id: str,
        tier: str = "starter"
    ) -> Dict:
        """Register a new agent with subscription tier"""
        # Initialize marketplace first
        market_state = await self.market.initialize_agent(agent_id)

        # Set subscription tier
        market_state["subscription_tier"] = tier
        market_state["subscription_start"] = datetime.utcnow().isoformat()

        # Initialize allowed systems
        system_states = {}
        for system_name in self.tier_systems[tier]:
            system = getattr(self, system_name)
            system_states[system_name] = await system.initialize_agent(agent_id)

        return {
            "market": market_state,
            "systems": system_states
        }

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve agent through allowed systems"""
        # Get marketplace state
        market_state = await self.market._load_state(agent_id)
        if not market_state:
            raise ValueError(f"Agent {agent_id} not registered")

        tier = market_state["subscription_tier"]
        allowed_systems = self.tier_systems[tier]

        # Evolve through allowed systems
        evolution_results = {}
        for system_name in allowed_systems:
            system = getattr(self, system_name)
            evolution_results[system_name] = await system.evolve_agent(agent_id)

        # Update marketplace
        market_update = await self.market.evolve_agent(agent_id)

        return {
            "market": market_update,
            "systems": evolution_results
        }

    async def upgrade_tier(
        self,
        agent_id: str,
        new_tier: str
    ) -> Dict:
        """Upgrade agent's subscription tier"""
        if new_tier not in self.tier_systems:
            raise ValueError(f"Invalid tier: {new_tier}")

        # Get current state
        market_state = await self.market._load_state(agent_id)
        if not market_state:
            raise ValueError(f"Agent {agent_id} not registered")

        old_tier = market_state["subscription_tier"]
        if old_tier == new_tier:
            return {"status": "unchanged"}

        # Calculate price difference
        old_price = self.market.get_tier_price(old_tier)
        new_price = self.market.get_tier_price(new_tier)
        price_diff = new_price - old_price

        # Update subscription
        market_state["subscription_tier"] = new_tier
        market_state["billing_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "upgrade",
            "from_tier": old_tier,
            "to_tier": new_tier,
            "amount": str(price_diff)
        })

        # Initialize new systems
        new_systems = set(self.tier_systems[new_tier]) - \
            set(self.tier_systems[old_tier])
        system_states = {}
        for system_name in new_systems:
            system = getattr(self, system_name)
            system_states[system_name] = await system.initialize_agent(agent_id)

        # Save market state
        await self.market._save_state(agent_id, market_state)

        return {
            "status": "upgraded",
            "old_tier": old_tier,
            "new_tier": new_tier,
            "price_difference": str(price_diff),
            "new_systems": list(system_states.keys())
        }

    def get_tier_info(self, tier: str) -> Dict:
        """Get information about a subscription tier"""
        if tier not in self.tier_systems:
            raise ValueError(f"Invalid tier: {tier}")

        return {
            "name": tier,
            "price": str(self.market.get_tier_price(tier)),
            "features": self.market.get_tier_features(tier),
            "systems": self.tier_systems[tier]
        }

    async def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get comprehensive agent information"""
        market_state = await self.market._load_state(agent_id)
        if not market_state:
            return None

        tier = market_state["subscription_tier"]
        system_states = {}

        for system_name in self.tier_systems[tier]:
            system = getattr(self, system_name)
            state = await system._load_state(agent_id)
            if state:
                system_states[system_name] = state

        return {
            "market": market_state,
            "systems": system_states
        }
