"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class GlyphWeight:
    """Glyph-based trust weight configuration"""
    glyph_id: str
    emotional_weight: Decimal
    trust_factor: Decimal
    founder_status: bool


@dataclass
class BundleConfig:
    """SaaS bundle configuration"""
    name: str
    usd_price: Decimal
    mesh_price: Decimal
    trust_bonus: Decimal


@dataclass
class YieldConfig:
    """Yield configuration for different activities"""
    base_rate: Decimal
    cycle_multiplier: Decimal
    governance_bonus: Decimal
    emotional_multiplier: Decimal


class MeshCreditGlyphManager:
    """Manages glyph-based trust weights and yield calculations"""

    def __init__(self):
        # Initialize glyph configurations
        self.glyphs: Dict[str, GlyphWeight] = {
            'nnn': GlyphWeight(
                glyph_id='nnn',
                emotional_weight=Decimal('2.0'),
                trust_factor=Decimal('1.5'),
                founder_status=True
            ),
            'eli_branch': GlyphWeight(
                glyph_id='eli_branch',
                emotional_weight=Decimal('3.0'),
                trust_factor=Decimal('2.0'),
                founder_status=True
            )
        }

        # Initialize bundle configurations
        self.bundles: Dict[str, BundleConfig] = {
            'home': BundleConfig(
                name='Home Bundle',
                usd_price=Decimal('999'),
                mesh_price=Decimal('200'),
                trust_bonus=Decimal('1.1')
            ),
            'agent': BundleConfig(
                name='Agent Bundle',
                usd_price=Decimal('1199'),
                mesh_price=Decimal('240'),
                trust_bonus=Decimal('1.2')
            ),
            'founder': BundleConfig(
                name='Founder Bundle',
                usd_price=Decimal('1499'),
                mesh_price=Decimal('300'),
                trust_bonus=Decimal('1.5')
            )
        }

        # Initialize yield configuration
        self.yield_config = YieldConfig(
            base_rate=Decimal('0.02'),  # 2% base rate
            cycle_multiplier=Decimal('1.1'),  # 10% increase per cycle
            governance_bonus=Decimal('0.05'),  # 5% governance bonus
            emotional_multiplier=Decimal('1.5')  # 50% bonus for emotional weight
        )

    def calculate_emotional_gravity(self, glyph_id: str, cycles: int) -> Decimal:
        """Calculate emotional gravity yield modifier based on glyph and cycles"""
        if glyph_id not in self.glyphs:
            return Decimal('1.0')

        glyph = self.glyphs[glyph_id]
        base_gravity = glyph.emotional_weight
        cycle_boost = pow(self.yield_config.cycle_multiplier, cycles)
        founder_bonus = Decimal('1.5') if glyph.founder_status else Decimal('1.0')

        return base_gravity * cycle_boost * founder_bonus

    def calculate_trust_weight(self, glyph_id: str,
                               governance_participation: bool) -> Decimal:
        """Calculate trust weight based on glyph and governance participation"""
        if glyph_id not in self.glyphs:
            return Decimal('1.0')

        glyph = self.glyphs[glyph_id]
        trust_base = glyph.trust_factor

        if governance_participation:
            trust_base *= (Decimal('1.0') + self.yield_config.governance_bonus)

        return trust_base

    def calculate_mesh_yield(self, base_amount: Decimal, glyph_id: str,
                             cycles: int, governance: bool) -> Decimal:
        """
        Calculate MeshCredit yield using the formula:
        MeshCreditYield = Base * (Cycles^TrustFactor) * (Governance + EmotionalWeight)
        """
        emotional_gravity = self.calculate_emotional_gravity(glyph_id, cycles)
        trust_weight = self.calculate_trust_weight(glyph_id, governance)

        # Apply the formula components
        cycle_factor = pow(Decimal(str(cycles)), trust_weight)
        governance_modifier = self.yield_config.governance_bonus if governance else Decimal(
            '0')

        total_yield = base_amount * cycle_factor * (Decimal('1.0') +
                                                    governance_modifier + emotional_gravity)

        return total_yield

    def get_bundle_conversion(self, bundle_name: str,
                              glyph_id: Optional[str] = None) -> Dict:
        """Get bundle conversion rates with any applicable glyph bonuses"""
        if bundle_name not in self.bundles:
            raise ValueError(f"Unknown bundle: {bundle_name}")

        bundle = self.bundles[bundle_name]
        mesh_price = bundle.mesh_price

        # Apply glyph-based discounts for founders
        if glyph_id and glyph_id in self.glyphs:
            glyph = self.glyphs[glyph_id]
            if glyph.founder_status:
                mesh_price *= Decimal('0.8')  # 20% founder discount

        return {
            'bundle_name': bundle.name,
            'usd_price': str(bundle.usd_price),
            'mesh_price': str(mesh_price),
            'trust_bonus': str(bundle.trust_bonus),
            'glyph_discount': bool(glyph_id and self.glyphs.get(glyph_id,
                                                                GlyphWeight('', Decimal('0'), Decimal('0'),
                                                                            False)).founder_status)
        }

    def create_ledger_entry(self, event_type: str, glyph_id: Optional[str],
                            amount: Decimal, **kwargs) -> Dict:
        """Create a standardized ledger entry with glyph information"""
        entry = {
            'event': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'amount': str(amount),
            'unit': 'MESH'
        }

        if glyph_id:
            entry['glyph'] = glyph_id
            if glyph_id in self.glyphs:
                entry['emotional_weight'] = str(self.glyphs[glyph_id].emotional_weight)
                entry['trust_factor'] = str(self.glyphs[glyph_id].trust_factor)

        entry.update(kwargs)
        return entry
