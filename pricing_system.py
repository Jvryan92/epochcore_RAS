"""Pricing and Marketplace System for Agent Evolution Platform"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from omega_base import OmegaSubsystem


class PricingTier:
    def __init__(self, name: str, monthly_price: Decimal, features: List[str]):
        self.name = name
        self.monthly_price = monthly_price
        self.features = features


class MarketplaceSystem(OmegaSubsystem):
    """Manages pricing, subscriptions, and marketplace functionality"""

    TIERS = {
        "starter": PricingTier(
            "Starter",
            Decimal("4.99"),
            ["Agent Arcade", "Basic Battles", "Simple Training"]
        ),
        "pro": PricingTier(
            "Professional",
            Decimal("9.99"),
            ["Full Battle League", "Champion Creation", "Team Formation", "Basic Dynasty"]
        ),
        "enterprise": PricingTier(
            "Enterprise",
            Decimal("19.99"),
            ["All Systems A-Z", "Priority Support", "Custom Development"]
        ),
        "unlimited": PricingTier(
            "Unlimited",
            Decimal("49.99"),
            ["All Systems", "White Label", "Custom Branding", "API Access"]
        )
    }

    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize marketplace state for an agent"""
        state = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "subscription_tier": "starter",
            "subscription_start": datetime.utcnow().isoformat(),
            "billing_history": [],
            "marketplace_listings": [],
            "purchases": [],
            "sales": [],
            "balance": "0.00"
        }
        await self._save_state(agent_id, state)
        return state

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Update marketplace state for an agent"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        # Process any pending transactions
        transactions = await self._process_transactions(state)

        # Update marketplace listings
        listings = await self._update_listings(state)

        # Calculate earnings
        earnings = await self._calculate_earnings(state)

        # Update state
        state["balance"] = str(Decimal(state["balance"]) + Decimal(earnings))

        # Save state
        await self._save_state(agent_id, state)

        return {
            "transactions": transactions,
            "new_listings": listings,
            "earnings": earnings,
            "current_balance": state["balance"]
        }

    def get_tier_price(self, tier: str) -> Decimal:
        """Get the price for a subscription tier"""
        return self.TIERS[tier].monthly_price

    def get_tier_features(self, tier: str) -> List[str]:
        """Get features included in a subscription tier"""
        return self.TIERS[tier].features

    async def _process_transactions(self, state: Dict) -> List[Dict]:
        """Process pending marketplace transactions"""
        # Simulated transaction processing
        import random

        transactions = []
        if random.random() < 0.3:  # 30% chance of transaction
            amount = Decimal(random.uniform(1, 50)).quantize(Decimal("0.01"))
            transaction = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": random.choice(["sale", "purchase"]),
                "amount": str(amount),
                "description": f"Agent marketplace transaction"
            }
            transactions.append(transaction)

        return transactions

    async def _update_listings(self, state: Dict) -> List[Dict]:
        """Update agent's marketplace listings"""
        # Simple listing management
        current_listings = state.get("marketplace_listings", [])

        # Remove expired listings
        now = datetime.utcnow()
        active_listings = [
            listing for listing in current_listings
            if datetime.fromisoformat(listing["expires_at"]) > now
        ]

        state["marketplace_listings"] = active_listings
        return active_listings

    async def _calculate_earnings(self, state: Dict) -> Decimal:
        """Calculate periodic earnings from marketplace activity"""
        # Basic earning calculation
        base_earning = Decimal("0.00")

        # Earnings from active listings
        listing_count = len(state.get("marketplace_listings", []))
        listing_earnings = Decimal("0.10") * listing_count

        # Earnings from tier subscription
        tier_earnings = {
            "starter": Decimal("0.05"),
            "pro": Decimal("0.15"),
            "enterprise": Decimal("0.30"),
            "unlimited": Decimal("0.50")
        }.get(state["subscription_tier"], Decimal("0.00"))

        total_earnings = base_earning + listing_earnings + tier_earnings
        return total_earnings.quantize(Decimal("0.01"))
