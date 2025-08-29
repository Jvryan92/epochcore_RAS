"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import hashlib
import time
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union


class RevenueStream(Enum):
    TOURNAMENT = "tournament"
    TRAINING = "training"
    ASSETS = "assets"
    SAAS = "saas"
    MESH_CREDIT = "mesh_credit"


@dataclass
class PricingTier:
    name: str
    monthly_cost: Decimal
    features: List[str]
    mesh_credit_multiplier: float
    performance_bonus_threshold: float


class RevenueSystem:
    def __init__(self):
        self.pricing_tiers = {
            "free": PricingTier(
                name="Free",
                monthly_cost=Decimal('0'),
                features=["Basic tournaments", "Standard mesh access", "Public assets"],
                mesh_credit_multiplier=1.0,
                performance_bonus_threshold=1.3
            ),
            "pro": PricingTier(
                name="Professional",
                monthly_cost=Decimal('49.99'),
                features=[
                    "Advanced tournaments",
                    "Enhanced mesh access",
                    "Custom assets",
                    "AI coaching",
                    "Priority support"
                ],
                mesh_credit_multiplier=2.0,
                performance_bonus_threshold=1.2
            ),
            "enterprise": PricingTier(
                name="Enterprise",
                monthly_cost=Decimal('199.99'),
                features=[
                    "Private tournaments",
                    "Dedicated mesh network",
                    "Custom agent training",
                    "White-label assets",
                    "24/7 support",
                    "API access"
                ],
                mesh_credit_multiplier=3.0,
                performance_bonus_threshold=1.1
            )
        }

        self.tournament_fees = {
            "daily": Decimal('1.00'),
            "weekly": Decimal('5.00'),
            "season": Decimal('20.00'),
            "championship": Decimal('50.00')
        }

        self.asset_pricing = {
            "basic_glyph": Decimal('0.99'),
            "animated_glyph": Decimal('2.99'),
            "custom_glyph": Decimal('9.99'),
            "glyph_pack": Decimal('19.99')
        }

        self.training_fees = {
            "basic_course": Decimal('29.99'),
            "advanced_course": Decimal('99.99'),
            "private_coaching": Decimal('199.99'),
            "team_training": Decimal('499.99')
        }

        self.saas_pricing = {
            "api_access": Decimal('99.99'),
            "mesh_deployment": Decimal('299.99'),
            "custom_integration": Decimal('999.99')
        }

    def calculate_mesh_credit_reward(
        self,
        base_amount: Decimal,
        performance_score: float,
        tier: str
    ) -> Decimal:
        """Calculate MeshCredit rewards based on performance and tier."""
        tier_info = self.pricing_tiers[tier]

        # Base reward with tier multiplier
        reward = base_amount * Decimal(str(tier_info.mesh_credit_multiplier))

        # Performance bonus
        if performance_score > tier_info.performance_bonus_threshold:
            bonus_multiplier = 1 + (performance_score -
                                    tier_info.performance_bonus_threshold)
            reward *= Decimal(str(bonus_multiplier))

        return reward

    def calculate_tournament_payout(
        self,
        tournament_type: str,
        participants: int,
        total_fees: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate tournament prize distribution."""
        if tournament_type == "daily":
            return {
                "first": total_fees * Decimal('0.5'),
                "second": total_fees * Decimal('0.3'),
                "third": total_fees * Decimal('0.2')
            }
        elif tournament_type == "championship":
            return {
                "first": total_fees * Decimal('0.4'),
                "second": total_fees * Decimal('0.25'),
                "third": total_fees * Decimal('0.15'),
                "fourth": total_fees * Decimal('0.1'),
                "fifth_to_tenth": total_fees * Decimal('0.1')
            }
        # Add more tournament types as needed

    def calculate_asset_royalties(
        self,
        creator_tier: str,
        asset_type: str,
        sales: int
    ) -> Decimal:
        """Calculate asset creation royalties."""
        base_price = self.asset_pricing[asset_type]
        tier_multiplier = self.pricing_tiers[creator_tier].mesh_credit_multiplier

        royalty_rate = Decimal('0.7')  # 70% to creator
        return (base_price * sales * royalty_rate) * Decimal(str(tier_multiplier))

    def generate_invoice_hash(self, invoice_data: Dict) -> str:
        """Generate audit-proof hash for transactions."""
        invoice_str = str(sorted(invoice_data.items()))
        return hashlib.sha256(invoice_str.encode()).hexdigest()

    def calculate_mesh_performance_bonus(
        self,
        success_rate: float,
        latency_efficiency: float,
        budget_efficiency: float
    ) -> float:
        """Calculate performance-based bonus multiplier."""
        performance_score = (success_rate + latency_efficiency +
                             budget_efficiency) / 3.0

        if performance_score > 1.3:
            return 1.5  # 50% bonus
        elif performance_score > 1.1:
            return 1.25  # 25% bonus
        elif performance_score > 1.0:
            return 1.1  # 10% bonus
        return 1.0
