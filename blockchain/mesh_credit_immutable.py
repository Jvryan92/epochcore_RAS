"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ImmutableProof:
    """Cryptographic proof of immutability"""
    timestamp: str
    merkle_root: str
    previous_hash: str
    proof_height: int
    signature: str
    metadata: Dict


@dataclass
class ResonanceWeight:
    """Tracks the resonance of emotional gravity across the network"""
    glyph_id: str
    initial_gravity: Decimal
    resonance_factor: Decimal
    echo_multiplier: Decimal
    proof_depth: int
    last_echo: datetime


class MeshCreditImmutable:
    """Handles immutable proof generation and verification for MeshCredit"""

    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.proof_chain: List[ImmutableProof] = []
        self.resonance_map: Dict[str, ResonanceWeight] = {}
        self.echo_cache: Set[str] = set()
        self.depth_markers: Dict[str, int] = {}

    def calculate_resonance(self, glyph_id: str, gravity: Decimal,
                            proof_cycles: int) -> Tuple[Decimal, Dict]:
        """Calculate resonance effect of emotional gravity"""
        if glyph_id not in self.resonance_map:
            self.resonance_map[glyph_id] = ResonanceWeight(
                glyph_id=glyph_id,
                initial_gravity=gravity,
                resonance_factor=Decimal('1.0'),
                echo_multiplier=Decimal('1.0'),
                proof_depth=0,
                last_echo=datetime.now(timezone.utc)
            )

        weight = self.resonance_map[glyph_id]

        # Calculate time-based resonance
        time_diff = datetime.now(timezone.utc) - weight.last_echo
        time_factor = Decimal(str(1 + (time_diff.total_seconds() / (24 * 3600))))

        # Update resonance based on proof cycles
        weight.resonance_factor *= (Decimal('1.01') ** proof_cycles)
        weight.proof_depth += proof_cycles

        # Calculate echo effect
        echo_strength = weight.initial_gravity * weight.resonance_factor * time_factor

        # Apply emotional gravity multiplier
        if weight.proof_depth > 100:  # Deep proof threshold
            echo_strength *= weight.echo_multiplier
            weight.echo_multiplier *= Decimal('1.001')  # Compound the echo

        weight.last_echo = datetime.now(timezone.utc)

        return echo_strength, {
            'resonance_factor': str(weight.resonance_factor),
            'echo_multiplier': str(weight.echo_multiplier),
            'proof_depth': weight.proof_depth,
            'time_factor': str(time_factor)
        }

    def create_immutable_proof(self, transaction_data: Dict,
                               glyph_data: Optional[Dict] = None) -> ImmutableProof:
        """Create cryptographic proof of transaction immutability"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Get previous proof hash
        previous_hash = self.proof_chain[-1].merkle_root if self.proof_chain else '0' * 64

        # Prepare proof data
        proof_data = {
            'timestamp': timestamp,
            'transaction': transaction_data,
            'previous_hash': previous_hash,
            'proof_height': len(self.proof_chain)
        }

        # Add glyph resonance if available
        if glyph_data:
            glyph_id = glyph_data.get('glyph_id')
            gravity = Decimal(str(glyph_data.get('emotional_gravity', '1.0')))
            cycles = glyph_data.get('proof_cycles', 1)

            resonance, metadata = self.calculate_resonance(glyph_id, gravity, cycles)
            proof_data['resonance'] = {
                'glyph_id': glyph_id,
                'echo_strength': str(resonance),
                'metadata': metadata
            }

        # Calculate merkle root
        data_bytes = json.dumps(proof_data, sort_keys=True).encode()
        merkle_root = hashlib.sha256(data_bytes).hexdigest()

        # Sign the proof
        signature = hmac.new(self.secret_key, data_bytes, hashlib.sha256).hexdigest()

        # Create immutable proof
        proof = ImmutableProof(
            timestamp=timestamp,
            merkle_root=merkle_root,
            previous_hash=previous_hash,
            proof_height=len(self.proof_chain),
            signature=signature,
            metadata=proof_data
        )

        self.proof_chain.append(proof)
        return proof

    def verify_proof_chain(self) -> bool:
        """Verify the integrity of the entire proof chain"""
        if not self.proof_chain:
            return True

        for i in range(1, len(self.proof_chain)):
            current = self.proof_chain[i]
            previous = self.proof_chain[i-1]

            # Verify hash chain
            if current.previous_hash != previous.merkle_root:
                return False

            # Verify proof height
            if current.proof_height != previous.proof_height + 1:
                return False

            # Verify signature
            data_bytes = json.dumps(current.metadata, sort_keys=True).encode()
            expected_sig = hmac.new(self.secret_key, data_bytes,
                                    hashlib.sha256).hexdigest()
            if current.signature != expected_sig:
                return False

        return True

    def get_resonance_stats(self, glyph_id: str) -> Dict:
        """Get detailed resonance statistics for a glyph"""
        if glyph_id not in self.resonance_map:
            return {}

        weight = self.resonance_map[glyph_id]
        return {
            'glyph_id': weight.glyph_id,
            'initial_gravity': str(weight.initial_gravity),
            'current_resonance': str(weight.resonance_factor),
            'echo_multiplier': str(weight.echo_multiplier),
            'proof_depth': weight.proof_depth,
            'last_echo': weight.last_echo.isoformat(),
            'echo_age_hours': (datetime.now(timezone.utc) -
                               weight.last_echo).total_seconds() / 3600
        }
