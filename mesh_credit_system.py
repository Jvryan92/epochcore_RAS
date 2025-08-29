"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List


@dataclass
class MeshCreditTransaction:
    timestamp: str
    credit_amount: Decimal
    reason: str
    performance_score: float
    transaction_hash: str


class MeshCreditSystem:
    def __init__(self):
        self.credit_rates = {
            # Participation Credits
            "tournament_entry": Decimal('10.0'),
            "tournament_win": Decimal('50.0'),
            "agent_training": Decimal('25.0'),
            "mesh_contribution": Decimal('15.0'),
            "asset_creation": Decimal('20.0'),

            # Performance Credits
            "high_performance": Decimal('30.0'),
            "innovation_bonus": Decimal('40.0'),
            "consistency_bonus": Decimal('35.0'),

            # Community Credits
            "helping_others": Decimal('15.0'),
            "bug_reporting": Decimal('20.0'),
            "feature_suggestion": Decimal('25.0')
        }

        self.credit_multipliers = {
            "free": Decimal('1.0'),
            "pro": Decimal('1.5'),
            "enterprise": Decimal('2.0')
        }

        self.performance_thresholds = {
            "excellent": 1.3,
            "good": 1.1,
            "standard": 1.0
        }

    def generate_timestamp(self) -> str:
        """Generate ISO format timestamp."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def calculate_credits(
        self,
        action: str,
        tier: str,
        performance_score: float,
        streak: int = 1
    ) -> Decimal:
        """Calculate MeshCredits for an action."""
        # Base credits
        base_credits = self.credit_rates.get(action, Decimal('0'))

        # Apply tier multiplier
        tier_multiplier = self.credit_multipliers.get(tier, Decimal('1.0'))
        credits = base_credits * tier_multiplier

        # Apply performance multiplier
        if performance_score >= self.performance_thresholds["excellent"]:
            credits *= Decimal('1.5')
        elif performance_score >= self.performance_thresholds["good"]:
            credits *= Decimal('1.25')

        # Apply streak bonus (max 2x)
        streak_multiplier = min(streak * Decimal('0.1') +
                                Decimal('1.0'), Decimal('2.0'))
        credits *= streak_multiplier

        return credits

    def create_transaction(
        self,
        credit_amount: Decimal,
        reason: str,
        performance_score: float
    ) -> MeshCreditTransaction:
        """Create a new MeshCredit transaction."""
        timestamp = self.generate_timestamp()

        # Create transaction data for hashing
        transaction_data = {
            "timestamp": timestamp,
            "amount": str(credit_amount),
            "reason": reason,
            "performance": str(performance_score)
        }

        # Generate hash
        transaction_str = str(sorted(transaction_data.items()))
        transaction_hash = hashlib.sha256(transaction_str.encode()).hexdigest()

        return MeshCreditTransaction(
            timestamp=timestamp,
            credit_amount=credit_amount,
            reason=reason,
            performance_score=performance_score,
            transaction_hash=transaction_hash
        )

    def calculate_credit_value(
        self,
        credits: Decimal,
        exchange_rate: Decimal
    ) -> Decimal:
        """Calculate monetary value of MeshCredits."""
        return credits * exchange_rate

    def get_credit_summary(self, transactions: List[MeshCreditTransaction]) -> Dict:
        """Generate summary of credit earnings."""
        return {
            "total_credits": sum(t.credit_amount for t in transactions),
            "transaction_count": len(transactions),
            "average_performance": sum(t.performance_score for t in transactions) / len(transactions) if transactions else 0,
            "last_transaction": max(transactions, key=lambda t: t.timestamp) if transactions else None
        }
