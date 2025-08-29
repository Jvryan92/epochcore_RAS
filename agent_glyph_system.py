"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List


class GlyphRank(Enum):
    INITIATE = "initiate"
    ADEPT = "adept"
    EXPERT = "expert"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    SOVEREIGN = "sovereign"
    OMEGA = "omega"


@dataclass
class GlyphToken:
    rank: GlyphRank
    mesh_power: Decimal
    creation_date: str
    token_hash: str
    attributes: Dict


class AgentGlyphSystem:
    def __init__(self):
        self.rank_requirements = {
            GlyphRank.INITIATE: {
                "mesh_score": 100,
                "tasks_completed": 10,
                "min_performance": 1.0
            },
            GlyphRank.ADEPT: {
                "mesh_score": 500,
                "tasks_completed": 50,
                "min_performance": 1.1
            },
            GlyphRank.EXPERT: {
                "mesh_score": 2000,
                "tasks_completed": 200,
                "min_performance": 1.2
            },
            GlyphRank.MASTER: {
                "mesh_score": 5000,
                "tasks_completed": 500,
                "min_performance": 1.3
            },
            GlyphRank.GRANDMASTER: {
                "mesh_score": 10000,
                "tasks_completed": 1000,
                "min_performance": 1.4
            },
            GlyphRank.SOVEREIGN: {
                "mesh_score": 25000,
                "tasks_completed": 2500,
                "min_performance": 1.5
            },
            GlyphRank.OMEGA: {
                "mesh_score": 100000,
                "tasks_completed": 10000,
                "min_performance": 2.0
            }
        }

        self.rank_rewards = {
            GlyphRank.INITIATE: Decimal('10.0'),
            GlyphRank.ADEPT: Decimal('25.0'),
            GlyphRank.EXPERT: Decimal('100.0'),
            GlyphRank.MASTER: Decimal('250.0'),
            GlyphRank.GRANDMASTER: Decimal('1000.0'),
            GlyphRank.SOVEREIGN: Decimal('2500.0'),
            GlyphRank.OMEGA: Decimal('10000.0')
        }

        # Special glyph attributes
        self.special_attributes = {
            "mesh_innovator": Decimal('500.0'),
            "performance_expert": Decimal('750.0'),
            "resource_optimizer": Decimal('1000.0'),
            "quantum_master": Decimal('2000.0'),
            "epoch_sovereign": Decimal('5000.0')
        }

    def mint_glyph_token(
        self,
        rank: GlyphRank,
        mesh_power: Decimal,
        attributes: Dict
    ) -> GlyphToken:
        """Create a new glyph token for an agent."""
        creation_date = datetime.now(timezone.utc).isoformat()

        # Generate unique hash incorporating all token data
        token_data = {
            "rank": rank.value,
            "mesh_power": str(mesh_power),
            "creation_date": creation_date,
            "attributes": str(sorted(attributes.items()))
        }
        token_hash = hashlib.sha256(
            str(sorted(token_data.items())).encode()
        ).hexdigest()

        return GlyphToken(
            rank=rank,
            mesh_power=mesh_power,
            creation_date=creation_date,
            token_hash=token_hash,
            attributes=attributes
        )

    def calculate_agent_payment(
        self,
        glyph: GlyphToken,
        performance_score: float,
        tasks_completed: int
    ) -> Decimal:
        """Calculate agent payment based on glyph rank and performance."""
        # Base payment from rank
        base_payment = self.rank_rewards[glyph.rank]

        # Performance multiplier
        perf_multiplier = Decimal(str(max(1.0, performance_score)))

        # Task completion bonus
        task_bonus = Decimal(str(tasks_completed)) * Decimal('0.1')

        # Special attribute bonuses
        attribute_bonus = sum(
            self.special_attributes[attr]
            for attr in glyph.attributes
            if attr in self.special_attributes
        )

        # Calculate total payment
        total_payment = (
            (base_payment * perf_multiplier) +
            task_bonus +
            attribute_bonus
        )

        return total_payment

    def evaluate_rank_up(
        self,
        current_rank: GlyphRank,
        agent_stats: Dict
    ) -> bool:
        """Check if agent qualifies for rank promotion."""
        if current_rank == GlyphRank.OMEGA:
            return False  # Already at max rank

        next_rank = list(GlyphRank)[list(GlyphRank).index(current_rank) + 1]
        requirements = self.rank_requirements[next_rank]

        return all(
            agent_stats.get(key, 0) >= value
            for key, value in requirements.items()
        )

    def generate_payment_record(
        self,
        agent_id: str,
        glyph: GlyphToken,
        payment: Decimal
    ) -> Dict:
        """Generate auditable payment record."""
        record = {
            "agent_id": agent_id,
            "glyph_hash": glyph.token_hash,
            "payment_amount": str(payment),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rank": glyph.rank.value
        }

        # Generate record hash
        record_hash = hashlib.sha256(
            str(sorted(record.items())).encode()
        ).hexdigest()
        record["record_hash"] = record_hash

        return record

    def calculate_mesh_power(
        self,
        rank: GlyphRank,
        attributes: Dict,
        performance_history: List[float]
    ) -> Decimal:
        """Calculate mesh power for glyph token."""
        # Base power from rank
        base_power = Decimal(str(list(GlyphRank).index(rank) + 1)) * Decimal('1000')

        # Attribute bonuses
        attribute_power = sum(
            self.special_attributes[attr]
            for attr in attributes
            if attr in self.special_attributes
        )

        # Performance bonus
        if performance_history:
            avg_performance = sum(performance_history) / len(performance_history)
            perf_bonus = Decimal(str(max(1.0, avg_performance))) * Decimal('500')
        else:
            perf_bonus = Decimal('0')

        return base_power + attribute_power + perf_bonus
