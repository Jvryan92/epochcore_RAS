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

from mesh_credit_system import MeshCreditSystem
from revenue_system import RevenueSystem
from tournament_economics import TournamentEconomics


@dataclass
class LaunchEvent:
    event_type: str
    credit_reward: Decimal
    bonus_multiplier: float
    duration_hours: int
    participants_max: int


class LaunchSequence:
    def __init__(self):
        self.tournament_eco = TournamentEconomics()
        self.mesh_credit = MeshCreditSystem()
        self.revenue = RevenueSystem()

        self.launch_events = {
            "genesis_tournament": LaunchEvent(
                event_type="championship",
                credit_reward=Decimal('10000.0'),
                bonus_multiplier=3.0,
                duration_hours=48,
                participants_max=1000
            ),
            "mesh_hackathon": LaunchEvent(
                event_type="innovation",
                credit_reward=Decimal('5000.0'),
                bonus_multiplier=2.5,
                duration_hours=72,
                participants_max=500
            ),
            "agent_olympics": LaunchEvent(
                event_type="competition",
                credit_reward=Decimal('7500.0'),
                bonus_multiplier=2.0,
                duration_hours=96,
                participants_max=2000
            )
        }

        self.early_bird_rewards = {
            "first_100": Decimal('1000.0'),
            "first_500": Decimal('500.0'),
            "first_1000": Decimal('250.0')
        }

        self.referral_bonuses = {
            "basic": Decimal('100.0'),
            "pro": Decimal('250.0'),
            "enterprise": Decimal('1000.0')
        }

    def calculate_launch_rewards(
        self,
        participant_number: int,
        tier: str,
        referral_count: int
    ) -> Dict:
        """Calculate total rewards for launch participants."""
        rewards = {
            "base_credits": Decimal('0'),
            "early_bird_bonus": Decimal('0'),
            "referral_bonus": Decimal('0'),
            "total_credits": Decimal('0')
        }

        # Early bird rewards
        if participant_number <= 100:
            rewards["early_bird_bonus"] = self.early_bird_rewards["first_100"]
        elif participant_number <= 500:
            rewards["early_bird_bonus"] = self.early_bird_rewards["first_500"]
        elif participant_number <= 1000:
            rewards["early_bird_bonus"] = self.early_bird_rewards["first_1000"]

        # Referral bonuses
        if referral_count > 0:
            rewards["referral_bonus"] = (
                self.referral_bonuses[tier] * Decimal(str(referral_count))
            )

        # Calculate total
        rewards["total_credits"] = (
            rewards["base_credits"] +
            rewards["early_bird_bonus"] +
            rewards["referral_bonus"]
        )

        return rewards

    def generate_launch_schedule(self) -> List[Dict]:
        """Generate optimized schedule of launch events."""
        schedule = []
        current_time = datetime.now(timezone.utc)

        for event_name, event in self.launch_events.items():
            schedule.append({
                "name": event_name,
                "start_time": current_time.isoformat(),
                "duration": event.duration_hours,
                "max_participants": event.participants_max,
                "base_reward": event.credit_reward,
                "bonus_multiplier": event.bonus_multiplier
            })
            # Space events 24 hours apart
            current_time = current_time.replace(
                hour=current_time.hour + 24 + event.duration_hours
            )

        return schedule

    def estimate_initial_distribution(
        self,
        expected_participants: int
    ) -> Dict[str, Decimal]:
        """Estimate initial MeshCredit distribution."""
        total_early_bird = (
            self.early_bird_rewards["first_100"] * 100 +
            self.early_bird_rewards["first_500"] * 400 +
            self.early_bird_rewards["first_1000"] * 500
        )

        # Estimate referrals (assume 20% bring referrals)
        estimated_referrals = int(expected_participants * 0.2)
        total_referral_bonus = (
            self.referral_bonuses["basic"] * Decimal(str(estimated_referrals))
        )

        # Tournament participation rewards
        tournament_rewards = Decimal('0')
        for event in self.launch_events.values():
            tournament_rewards += (
                event.credit_reward *
                Decimal(str(min(expected_participants, event.participants_max)))
            )

        return {
            "early_bird_total": total_early_bird,
            "referral_total": total_referral_bonus,
            "tournament_total": tournament_rewards,
            "total_distribution": (
                total_early_bird + total_referral_bonus + tournament_rewards
            )
        }

    def generate_launch_report(
        self,
        event_name: str,
        participants: List[Dict]
    ) -> Dict:
        """Generate detailed report for launch event."""
        total_credits = sum(
            p["rewards"]["total_credits"] for p in participants
        )
        avg_credits = total_credits / len(participants)

        report = {
            "event_name": event_name,
            "participant_count": len(participants),
            "total_credits_awarded": total_credits,
            "average_credits_per_participant": avg_credits,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Generate report hash
        report_hash = hashlib.sha256(
            str(sorted(report.items())).encode()
        ).hexdigest()
        report["report_hash"] = report_hash

        return report
