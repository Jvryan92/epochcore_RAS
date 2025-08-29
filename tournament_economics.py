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
class TournamentPrize:
    rank: int
    mesh_credits: Decimal
    bonus_rewards: Dict
    prize_hash: str


class TournamentEconomics:
    def __init__(self):
        self.entry_fees = {
            "daily": Decimal('5.0'),
            "weekly": Decimal('25.0'),
            "monthly": Decimal('75.0'),
            "seasonal": Decimal('200.0'),
            "championship": Decimal('500.0')
        }

        self.credit_rewards = {
            "daily": {
                1: Decimal('100.0'),
                2: Decimal('50.0'),
                3: Decimal('25.0')
            },
            "weekly": {
                1: Decimal('500.0'),
                2: Decimal('250.0'),
                3: Decimal('125.0')
            },
            "monthly": {
                1: Decimal('2000.0'),
                2: Decimal('1000.0'),
                3: Decimal('500.0')
            },
            "seasonal": {
                1: Decimal('5000.0'),
                2: Decimal('2500.0'),
                3: Decimal('1250.0')
            },
            "championship": {
                1: Decimal('10000.0'),
                2: Decimal('5000.0'),
                3: Decimal('2500.0')
            }
        }

        self.bonus_rewards = {
            "perfect_score": Decimal('1000.0'),
            "win_streak": Decimal('500.0'),
            "underdog_victory": Decimal('750.0'),
            "audience_favorite": Decimal('250.0')
        }

    def calculate_prize_pool(
        self,
        tournament_type: str,
        participants: int,
        sponsor_bonus: Decimal = Decimal('0')
    ) -> Decimal:
        """Calculate total prize pool including entry fees and sponsorships."""
        base_pool = self.entry_fees[tournament_type] * Decimal(str(participants))
        return base_pool + sponsor_bonus

    def distribute_prizes(
        self,
        tournament_type: str,
        prize_pool: Decimal,
        rankings: List[Dict]
    ) -> List[TournamentPrize]:
        """Calculate prize distribution for tournament winners."""
        prizes = []
        base_rewards = self.credit_rewards[tournament_type]

        for rank, player in enumerate(rankings, 1):
            if rank in base_rewards:
                # Calculate mesh credits
                credits = base_rewards[rank]

                # Calculate any bonus rewards
                bonuses = {}
                if player.get("perfect_score"):
                    bonuses["perfect"] = self.bonus_rewards["perfect_score"]
                if player.get("streak"):
                    bonuses["streak"] = self.bonus_rewards["win_streak"]
                if player.get("underdog"):
                    bonuses["underdog"] = self.bonus_rewards["underdog_victory"]
                if player.get("favorite"):
                    bonuses["favorite"] = self.bonus_rewards["audience_favorite"]

                # Generate prize hash
                prize_data = {
                    "rank": rank,
                    "credits": str(credits),
                    "bonuses": str(bonuses),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                prize_hash = hashlib.sha256(
                    str(sorted(prize_data.items())).encode()
                ).hexdigest()

                prizes.append(
                    TournamentPrize(
                        rank=rank,
                        mesh_credits=credits,
                        bonus_rewards=bonuses,
                        prize_hash=prize_hash
                    )
                )

        return prizes

    def calculate_roi(
        self,
        entry_fee: Decimal,
        total_winnings: Decimal
    ) -> float:
        """Calculate Return on Investment for tournament participation."""
        if entry_fee == Decimal('0'):
            return 0.0
        return float((total_winnings - entry_fee) / entry_fee * 100)

    def generate_payout_report(
        self,
        tournament_type: str,
        prizes: List[TournamentPrize]
    ) -> Dict:
        """Generate detailed payout report with verification hashes."""
        total_credits = sum(p.mesh_credits for p in prizes)
        total_bonuses = sum(
            sum(b for b in p.bonus_rewards.values())
            for p in prizes
        )

        report = {
            "tournament_type": tournament_type,
            "total_prizes_awarded": total_credits + total_bonuses,
            "prize_count": len(prizes),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prize_hashes": [p.prize_hash for p in prizes]
        }

        # Generate report hash
        report_hash = hashlib.sha256(
            str(sorted(report.items())).encode()
        ).hexdigest()
        report["report_hash"] = report_hash

        return report
