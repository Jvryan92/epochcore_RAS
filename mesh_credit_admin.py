"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import time
from typing import Optional

from mesh_credit import MeshCredit, MeshGlyph
from mesh_credit_game import MeshCreditGame


class MeshCreditAdmin:
    """Administrative interface for MeshCredit system"""

    def __init__(self):
        self.game = MeshCreditGame()
        self.admin_wallet = "MESH_ADMIN_GENESIS"
        self.conversion_rate = 10000  # 1 USD = 10000 MeshCredits
        self.penny_ratio = 0.25  # 25% of investment goes to penny backing

    def process_investment(self, usd_amount: float, investor_id: str) -> Optional[dict]:
        """Process a USD investment into MeshCredits"""
        if usd_amount <= 0:
            return None

        # Calculate MeshCredit amount
        mesh_amount = usd_amount * self.conversion_rate

        # Calculate penny backing
        penny_amount = int(usd_amount * 100 * self.penny_ratio)  # Convert to pennies

        # Add penny backing
        self.game.mesh.back_with_pennies(penny_amount)

        # Create investor profile if needed
        if investor_id not in self.game.players:
            self.game.create_player(investor_id)

        # Create investment glyph
        investor_glyph = MeshGlyph(
            glyph_id=f"INVESTOR_{int(time.time())}",
            trust_weight=min(1.0, usd_amount / 1000),  # Scale with investment
            emotional_resonance=0.8,
            founder_status=False
        )

        # Add glyph to investor
        self.game.players[investor_id].glyphs.append(investor_glyph)

        # Initialize admin wallet if needed
        success = self.game.mesh.add_transaction(
            "GENESIS",
            self.admin_wallet,
            self.game.mesh.total_supply
        )

        if not success:
            return None

        # Transfer MeshCredits to investor
        success = self.game.mesh.add_transaction(
            self.admin_wallet,
            self.game.players[investor_id].wallet_id,
            mesh_amount
        )

        if not success:
            return None

        return {
            'usd_amount': usd_amount,
            'mesh_amount': mesh_amount,
            'penny_backing': penny_amount,
            'wallet_id': self.game.players[investor_id].wallet_id,
            'investment_glyph': investor_glyph.glyph_id,
            'new_balance': self.game.mesh.get_balance(
                self.game.players[investor_id].wallet_id
            )
        }

    def get_system_stats(self) -> dict:
        """Get overall MeshCredit system statistics"""
        return {
            'total_supply': self.game.mesh.total_supply,
            'current_supply': self.game.mesh.current_supply,
            'penny_backing': self.game.mesh.backing_pennies,
            'stability_ratio': self.game.mesh.backing_pennies / (self.game.mesh.current_supply or 1),
            'active_players': len(self.game.players),
            'total_blocks': len(self.game.mesh.chain),
            'conversion_rate': self.conversion_rate,
            'min_gravity': self.game.mesh.min_gravity
        }
