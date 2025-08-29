"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from mesh_credit import MeshGlyph
from mesh_credit_game import MeshCreditGame


@dataclass
class MeshTranche:
    """Represents a tranche of MeshCredit investment"""
    tranche_id: str
    risk_level: str  # "AAA", "AA", "A", "BBB", "BB", "B"
    mesh_amount: float
    penny_backing: int
    yield_rate: float  # Annual yield rate
    lock_period: int  # Lock period in days
    creation_time: float
    owner_wallet: Optional[str] = None
    is_locked: bool = True


class MeshTrancheMaster:
    """Manages MeshCredit tranches and investment bundles"""

    def __init__(self, game: MeshCreditGame):
        self.game = game
        self.tranches: Dict[str, MeshTranche] = {}
        self.risk_configs = {
            "AAA": {
                "yield_rate": 0.12,  # 12% APY
                "backing_ratio": 0.40,  # 40% penny backing
                "lock_period": 90,  # 90 days
                "min_amount": 50_000  # Minimum 50K MESH
            },
            "AA": {
                "yield_rate": 0.15,
                "backing_ratio": 0.35,
                "lock_period": 60,
                "min_amount": 25_000
            },
            "A": {
                "yield_rate": 0.18,
                "backing_ratio": 0.30,
                "lock_period": 45,
                "min_amount": 10_000
            },
            "BBB": {
                "yield_rate": 0.22,
                "backing_ratio": 0.25,
                "lock_period": 30,
                "min_amount": 5_000
            },
            "BB": {
                "yield_rate": 0.28,
                "backing_ratio": 0.20,
                "lock_period": 15,
                "min_amount": 2_500
            },
            "B": {
                "yield_rate": 0.35,
                "backing_ratio": 0.15,
                "lock_period": 7,
                "min_amount": 1_000
            }
        }

    def create_tranche(self, risk_level: str, mesh_amount: float) -> Optional[MeshTranche]:
        """Create a new investment tranche"""
        if risk_level not in self.risk_configs:
            return None

        config = self.risk_configs[risk_level]

        # Validate minimum amount
        if mesh_amount < config["min_amount"]:
            return None

        # Calculate penny backing
        # Convert to pennies
        penny_backing = int(mesh_amount * config["backing_ratio"] * 0.01)

        tranche_id = f"TRANCHE_{risk_level}_{int(time.time())}"

        tranche = MeshTranche(
            tranche_id=tranche_id,
            risk_level=risk_level,
            mesh_amount=mesh_amount,
            penny_backing=penny_backing,
            yield_rate=config["yield_rate"],
            lock_period=config["lock_period"],
            creation_time=time.time()
        )

        self.tranches[tranche_id] = tranche
        return tranche

    def purchase_tranche(self, tranche_id: str, buyer_id: str) -> Optional[dict]:
        """Purchase an available tranche"""
        if tranche_id not in self.tranches:
            return None

        tranche = self.tranches[tranche_id]
        if tranche.owner_wallet or not tranche.is_locked:
            return None

        if buyer_id not in self.game.players:
            return None

        buyer_wallet = self.game.players[buyer_id].wallet_id

        # Create investment glyph
        investor_glyph = MeshGlyph(
            glyph_id=f"TRANCHE_HOLDER_{tranche_id}",
            trust_weight=min(1.0, tranche.mesh_amount / 100_000),
            emotional_resonance=0.9,
            founder_status=False
        )

        # Add glyph to buyer
        self.game.players[buyer_id].glyphs.append(investor_glyph)

        # Transfer MeshCredits to escrow
        success = self.game.transfer_mesh(
            buyer_id,
            "MESH_TRANCHE_ESCROW",
            tranche.mesh_amount
        )

        if not success:
            return None

        # Update tranche ownership
        tranche.owner_wallet = buyer_wallet

        return {
            'tranche_id': tranche_id,
            'mesh_amount': tranche.mesh_amount,
            'risk_level': tranche.risk_level,
            'yield_rate': tranche.yield_rate,
            'lock_period': tranche.lock_period,
            'penny_backing': tranche.penny_backing,
            'unlock_time': tranche.creation_time + (tranche.lock_period * 86400),
            'investor_glyph': investor_glyph.glyph_id
        }

    def calculate_yield(self, tranche_id: str) -> Optional[float]:
        """Calculate current yield for a tranche"""
        if tranche_id not in self.tranches:
            return None

        tranche = self.tranches[tranche_id]
        if not tranche.owner_wallet:
            return None

        # Calculate time held in years
        years_held = (time.time() - tranche.creation_time) / (365 * 86400)

        # Calculate yield
        return tranche.mesh_amount * tranche.yield_rate * years_held

    def unlock_tranche(self, tranche_id: str) -> Optional[dict]:
        """Unlock a tranche after lock period"""
        if tranche_id not in self.tranches:
            return None

        tranche = self.tranches[tranche_id]
        if not tranche.owner_wallet or not tranche.is_locked:
            return None

        # Check if lock period has passed
        if time.time() < tranche.creation_time + (tranche.lock_period * 86400):
            return None

        # Calculate yield
        earned_yield = self.calculate_yield(tranche_id)
        if earned_yield is None:
            return None

        # Transfer principal + yield from escrow
        success = self.game.mesh.add_transaction(
            "MESH_TRANCHE_ESCROW",
            tranche.owner_wallet,
            tranche.mesh_amount + earned_yield
        )

        if not success:
            return None

        tranche.is_locked = False

        return {
            'tranche_id': tranche_id,
            'principal': tranche.mesh_amount,
            'yield_earned': earned_yield,
            'total_return': tranche.mesh_amount + earned_yield,
            'holding_period': time.time() - tranche.creation_time
        }

    def get_available_tranches(self) -> List[dict]:
        """Get list of available tranches for purchase"""
        available = []
        for tranche_id, tranche in self.tranches.items():
            if not tranche.owner_wallet and tranche.is_locked:
                available.append({
                    'tranche_id': tranche_id,
                    'risk_level': tranche.risk_level,
                    'mesh_amount': tranche.mesh_amount,
                    'yield_rate': tranche.yield_rate,
                    'lock_period': tranche.lock_period,
                    'penny_backing': tranche.penny_backing
                })
        return available
