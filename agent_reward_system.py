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

from agent_glyph_system import GlyphRank, GlyphToken
from mesh_credit_system import MeshCreditSystem


@dataclass
class AgentReward:
    mesh_credits: Decimal
    performance_bonus: Decimal
    innovation_bonus: Decimal
    collaboration_bonus: Decimal
    total_reward: Decimal
    reward_hash: str


class AgentRewardSystem:
    def __init__(self):
        self.mesh_credit = MeshCreditSystem()

        # Base MeshCredit rewards by rank
        self.rank_credits = {
            GlyphRank.INITIATE: Decimal('50.0'),
            GlyphRank.ADEPT: Decimal('150.0'),
            GlyphRank.EXPERT: Decimal('500.0'),
            GlyphRank.MASTER: Decimal('1500.0'),
            GlyphRank.GRANDMASTER: Decimal('5000.0'),
            GlyphRank.SOVEREIGN: Decimal('15000.0'),
            GlyphRank.OMEGA: Decimal('50000.0')
        }

        # Innovation bonuses
        self.innovation_rewards = {
            "new_pattern": Decimal('100.0'),
            "efficiency_gain": Decimal('250.0'),
            "breakthrough": Decimal('1000.0'),
            "mesh_evolution": Decimal('5000.0')
        }

        # Collaboration bonuses
        self.collaboration_rewards = {
            "mesh_assist": Decimal('50.0'),
            "knowledge_share": Decimal('150.0'),
            "joint_solution": Decimal('500.0'),
            "mesh_synergy": Decimal('1000.0')
        }

        # Performance thresholds for bonus multipliers
        self.performance_multipliers = {
            1.5: Decimal('2.0'),  # 2x rewards for 1.5+ performance
            1.3: Decimal('1.5'),  # 1.5x rewards for 1.3+ performance
            1.1: Decimal('1.25')  # 1.25x rewards for 1.1+ performance
        }

    def calculate_agent_rewards(
        self,
        glyph: GlyphToken,
        performance_score: float,
        innovations: List[str],
        collaborations: List[str]
    ) -> AgentReward:
        """Calculate total MeshCredit rewards for an agent."""
        # Base credits from rank
        base_credits = self.rank_credits[glyph.rank]

        # Performance bonus
        performance_multiplier = Decimal('1.0')
        for threshold, multiplier in self.performance_multipliers.items():
            if performance_score >= threshold:
                performance_multiplier = multiplier
                break
        performance_bonus = base_credits * (performance_multiplier - Decimal('1.0'))

        # Innovation bonuses
        innovation_bonus = sum(
            self.innovation_rewards[innovation]
            for innovation in innovations
            if innovation in self.innovation_rewards
        )

        # Collaboration bonuses
        collaboration_bonus = sum(
            self.collaboration_rewards[collab]
            for collab in collaborations
            if collab in self.collaboration_rewards
        )

        # Calculate total
        total_reward = (
            base_credits +
            performance_bonus +
            innovation_bonus +
            collaboration_bonus
        )

        # Generate reward hash
        reward_data = {
            "base_credits": str(base_credits),
            "performance_bonus": str(performance_bonus),
            "innovation_bonus": str(innovation_bonus),
            "collaboration_bonus": str(collaboration_bonus),
            "total_reward": str(total_reward),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "glyph_hash": glyph.token_hash
        }
        reward_hash = hashlib.sha256(
            str(sorted(reward_data.items())).encode()
        ).hexdigest()

        return AgentReward(
            mesh_credits=base_credits,
            performance_bonus=performance_bonus,
            innovation_bonus=innovation_bonus,
            collaboration_bonus=collaboration_bonus,
            total_reward=total_reward,
            reward_hash=reward_hash
        )

    def apply_special_bonuses(
        self,
        reward: AgentReward,
        glyph: GlyphToken
    ) -> AgentReward:
        """Apply special bonuses based on glyph attributes."""
        bonus_multiplier = Decimal('1.0')

        # Special attribute bonuses
        if "mesh_innovator" in glyph.attributes:
            bonus_multiplier += Decimal('0.2')  # +20%
        if "quantum_master" in glyph.attributes:
            bonus_multiplier += Decimal('0.3')  # +30%
        if "epoch_sovereign" in glyph.attributes:
            bonus_multiplier += Decimal('0.5')  # +50%

        # Apply multiplier to total reward
        new_total = reward.total_reward * bonus_multiplier

        # Generate new hash for modified reward
        reward_data = {
            "original_hash": reward.reward_hash,
            "bonus_multiplier": str(bonus_multiplier),
            "new_total": str(new_total),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        new_hash = hashlib.sha256(
            str(sorted(reward_data.items())).encode()
        ).hexdigest()

        return AgentReward(
            mesh_credits=reward.mesh_credits,
            performance_bonus=reward.performance_bonus,
            innovation_bonus=reward.innovation_bonus,
            collaboration_bonus=reward.collaboration_bonus,
            total_reward=new_total,
            reward_hash=new_hash
        )

    def generate_reward_report(
        self,
        agent_id: str,
        glyph: GlyphToken,
        reward: AgentReward
    ) -> Dict:
        """Generate detailed reward report."""
        report = {
            "agent_id": agent_id,
            "glyph_rank": glyph.rank.value,
            "glyph_hash": glyph.token_hash,
            "reward_breakdown": {
                "base_credits": str(reward.mesh_credits),
                "performance_bonus": str(reward.performance_bonus),
                "innovation_bonus": str(reward.innovation_bonus),
                "collaboration_bonus": str(reward.collaboration_bonus)
            },
            "total_reward": str(reward.total_reward),
            "reward_hash": reward.reward_hash,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Generate report hash
        report_hash = hashlib.sha256(
            str(sorted(report.items())).encode()
        ).hexdigest()
        report["report_hash"] = report_hash

        return report
