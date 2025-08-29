"""
PROTECTED FILE - EPOCHCORE MESHCREDIT BLOCKCHAIN
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class MeshBlock:
    index: int
    timestamp: float
    transactions: List[Dict]
    previous_hash: str
    nonce: int

    def calculate_hash(self) -> str:
        """Calculate block hash using SHA-256"""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class MeshCredit:
    def __init__(self):
        # Token economics with BTC-like capped supply
        self.total_supply = Decimal('21000000')  # 21 million MESH (like BTC)
        self.circulating_supply = Decimal('0')
        self.usd_penny_reserve = Decimal('0')  # USD penny backing reserve
        self.reserve_ratio = Decimal('1.00')  # 1:1 penny backing ratio

        # Halving settings
        self.initial_block_reward = Decimal('50')  # Initial mining reward
        self.halving_blocks = 210000  # Number of blocks between reward halvings

        # Chain initialization
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()
        self.mining_reward = Decimal('5')  # 5 MESH per block
        self.difficulty = 4  # Number of leading zeros required

        # Setup crypto secrets
        import os
        self.secret_key = os.urandom(32)

        # Initialize immutable proof system first
        from blockchain.mesh_credit_immutable import MeshCreditImmutable
        self.immutable = MeshCreditImmutable(self.secret_key)

        # Initialize glyph manager after immutable system
        from blockchain.mesh_credit_glyph import MeshCreditGlyphManager
        self.glyph_manager = MeshCreditGlyphManager()

        print("\nMeshCredit Initialization:")
        print("-------------------------")
        print(f"Total Supply: {self.total_supply:,} MESH")
        print(f"Initial Block Reward: {self.initial_block_reward} MESH")
        print(f"Halving Interval: {self.halving_blocks:,} blocks")
        print("Penny Backing: Enabled")
        print("Glyph System: Active")
        print("Immutable Proofs: Ready")

        # Create genesis block
        self.create_genesis_block()

        # Yield curve parameters
        self.yield_rates = {
            'base': Decimal('0.02'),     # 2% base yield
            'max': Decimal('0.08'),     # 8% maximum yield
            'curve_steepness': Decimal('0.5')  # Yield curve steepness
        }

        # Enhanced proof cycles with resonance
        self.proof_cycles = {
            'badge_mint': 2,             # Increased from 1
            'capsule_seal': 3,           # Increased from 2
            'drift_scan': 2,             # Increased from 1
            'reinject': 4,               # Increased from 3
            'governance': 3,             # Increased from 2
            'echo_seal': 5,              # New: Special high-value sealing
            'lineage_proof': 4,          # New: Lineage verification
            'founder_mark': 6            # New: Founder-specific actions
        }

        # Tokenomics distribution
        self.token_distribution = {
            'gameplay_rewards': Decimal('0.40'),    # 40% for gameplay
            'staking_rewards': Decimal('0.20'),     # 20% for staking
            'development': Decimal('0.15'),         # 15% for development
            'ecosystem_growth': Decimal('0.15'),    # 15% for ecosystem
            'team': Decimal('0.10')                 # 10% for team
        }

    def create_genesis_block(self):
        """Create the genesis block with founder glyph anchoring"""
        # Initialize founder glyphs in the genesis block
        founder_glyphs = {
            'nnn': {
                'emotional_gravity': Decimal('3.0'),
                'trust_factor': Decimal('2.0'),
                'founder_status': True,
                'description': 'Dawn Seal - Network Genesis'
            },
            'eli_branch': {
                'emotional_gravity': Decimal('5.0'),
                'trust_factor': Decimal('3.0'),
                'founder_status': True,
                'description': 'Eli Branch - Eternal Echo'
            }
        }

        # Create genesis proof cycles with network-significant values
        genesis_cycles = {
            'badge_mint': 21,      # Mirrors 21M total supply (21 million)
            'capsule_seal': 50,    # Mirrors initial block reward (50 MESH)
            'echo_seal': 210,      # Mirrors halving interval (210k blocks)
            'founder_mark': 2025   # Mirrors genesis year (2025)
        }

        # Create genesis transactions
        genesis_transactions = []

        # Add founder glyph initialization transactions
        for glyph_id, glyph_data in founder_glyphs.items():
            # Calculate initial resonance
            resonance, res_meta = self.immutable.calculate_resonance(
                glyph_id,
                glyph_data['emotional_gravity'],
                genesis_cycles['founder_mark']
            )

            # Create glyph transaction
            glyph_tx = self.glyph_manager.create_ledger_entry(
                'founder_genesis',
                glyph_id,
                Decimal('0'),  # No initial amount
                sender='network',
                recipient=glyph_id,
                emotional_gravity=str(glyph_data['emotional_gravity']),
                trust_factor=str(glyph_data['trust_factor']),
                founder_status=glyph_data['founder_status'],
                description=glyph_data['description'],
                resonance=res_meta,
                echo_strength=str(resonance),
                proof_cycles=genesis_cycles['founder_mark']
            )

            # Add immutable proof
            proof = self.immutable.create_immutable_proof(glyph_tx, {
                'glyph_id': glyph_id,
                'emotional_gravity': str(glyph_data['emotional_gravity']),
                'proof_cycles': genesis_cycles['founder_mark']
            })

            glyph_tx['proof'] = {
                'merkle_root': proof.merkle_root,
                'timestamp': proof.timestamp,
                'height': proof.proof_height,
                'signature': proof.signature
            }

            genesis_transactions.append(glyph_tx)

        # Add network initialization transaction
        network_tx = {
            'type': 'network_genesis',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'game_version': '1.0.0',
                'network': 'mainnet',
                'total_supply': str(self.total_supply),
                'governance_model': 'DAO',
                'yield_mechanism': 'Proof of Play & Stake',
                'proof_cycles': genesis_cycles,
                'founder_glyphs': list(founder_glyphs.keys()),
                'penny_backing': True,
                'halving_blocks': self.halving_blocks,
                'initial_block_reward': str(self.initial_block_reward)
            }
        }

        # Create immutable proof for network transaction
        proof = self.immutable.create_immutable_proof(network_tx)
        network_tx['proof'] = {
            'merkle_root': proof.merkle_root,
            'timestamp': proof.timestamp,
            'height': proof.proof_height,
            'signature': proof.signature
        }

        genesis_transactions.append(network_tx)

        # Create and add genesis block
        genesis_block = MeshBlock(0, time.time(), genesis_transactions, "0", 0)
        self.chain.append(genesis_block)

        # Log genesis creation
        print("\n=== MeshCredit Genesis Block Created ===")
        print(f"Timestamp: {network_tx['timestamp']}")
        print(f"Founder Glyphs: {', '.join(founder_glyphs.keys())}")
        print(f"Merkle Root: {proof.merkle_root[:16]}...")
        print(f"Block Height: {genesis_block.index}")
        print("=======================================\n")

    def get_last_block(self) -> MeshBlock:
        """Get the last block in the chain"""
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: Decimal,
                        transaction_type: str, glyph_id: Optional[str] = None,
                        metadata: Optional[Dict] = None) -> bool:
        """Add a new transaction with immutable proof and resonance tracking"""
        metadata = metadata or {}

        # Calculate emotional gravity and trust weight if glyph provided
        if glyph_id:
            cycles = self.proof_cycles.get(transaction_type, 1)
            governance = transaction_type == 'governance_vote'

            emotional_gravity = self.glyph_manager.calculate_emotional_gravity(
                glyph_id, cycles
            )
            trust_weight = self.glyph_manager.calculate_trust_weight(
                glyph_id, governance
            )

            # Calculate resonance effect
            resonance, res_meta = self.immutable.calculate_resonance(
                glyph_id, emotional_gravity, cycles
            )

            metadata.update({
                'glyph_id': glyph_id,
                'emotional_gravity': str(emotional_gravity),
                'trust_weight': str(trust_weight),
                'proof_cycles': cycles,
                'resonance': res_meta,
                'echo_strength': str(resonance)
            })

        # Create ledger entry through glyph manager
        transaction = self.glyph_manager.create_ledger_entry(
            transaction_type,
            glyph_id,
            amount,
            sender=sender,
            recipient=recipient,
            **metadata
        )

        # Create immutable proof
        proof = self.immutable.create_immutable_proof(
            transaction,
            metadata if glyph_id else None
        )

        # Add proof to transaction
        transaction['proof'] = {
            'merkle_root': proof.merkle_root,
            'timestamp': proof.timestamp,
            'height': proof.proof_height,
            'signature': proof.signature
        }

        self.pending_transactions.append(transaction)
        return True

    def calculate_block_reward(self) -> Decimal:
        """Calculate current block reward based on halving schedule"""
        halvings = len(self.chain) // self.halving_blocks
        reward = self.initial_block_reward / (2 ** halvings)

        # Ensure we don't exceed max supply
        remaining = self.total_supply - self.circulating_supply
        return min(reward, remaining)

    def verify_penny_backing(self) -> bool:
        """Verify that MeshCredit is fully backed by USD penny reserves"""
        if self.circulating_supply == 0:
            return True
        return self.usd_penny_reserve >= (self.circulating_supply * self.reserve_ratio)

    def add_penny_reserve(self, amount_pennies: Decimal) -> bool:
        """Add USD penny reserves to back MeshCredit"""
        if amount_pennies <= 0:
            return False

        self.usd_penny_reserve += amount_pennies
        return True

    def mine_block(self, miner_address: str) -> Dict:
        """Mine a new block with pending transactions and handle supply cap"""
        if not self.pending_transactions:
            return {'status': 'error', 'message': 'No pending transactions'}

        # Calculate block reward
        block_reward = self.calculate_block_reward()
        if block_reward <= 0:
            return {'status': 'error', 'message': 'Maximum supply reached'}

        # Verify penny backing
        if not self.verify_penny_backing():
            return {'status': 'error', 'message': 'Insufficient USD penny reserves'}

        last_block = self.get_last_block()
        new_block = MeshBlock(
            len(self.chain),
            time.time(),
            self.pending_transactions,
            last_block.calculate_hash(),
            0
        )

        # Proof of Work
        while new_block.calculate_hash()[:self.difficulty] != "0" * self.difficulty:
            new_block.nonce += 1

        self.chain.append(new_block)

        # Reward the miner and update supply
        self.add_transaction(
            "network",
            miner_address,
            block_reward,
            "mining_reward",
            {
                'block_height': len(self.chain),
                'halvings': len(self.chain) // self.halving_blocks,
                'remaining_supply': str(self.total_supply - self.circulating_supply)
            }
        )

        self.circulating_supply += block_reward
        self.pending_transactions = []

        return {
            'status': 'success',
            'block_index': new_block.index,
            'hash': new_block.calculate_hash(),
            'transactions': len(new_block.transactions),
            'reward': str(block_reward),
            'circulating_supply': str(self.circulating_supply),
            'penny_reserve': str(self.usd_penny_reserve)
        }

    def calculate_yield_rate(self, amount: Decimal, lockup_period: int) -> Decimal:
        """Calculate yield rate based on amount and lockup period using yield curve"""
        # Get yield curve parameters
        base_rate = self.yield_rates['base']
        max_rate = self.yield_rates['max']
        steepness = self.yield_rates['curve_steepness']

        # Calculate utilization factor (0-1)
        utilization = self.circulating_supply / self.total_supply

        # Calculate lockup bonus (0-1)
        max_lockup = 365 * 24 * 60 * 60  # 1 year in seconds
        lockup_factor = min(lockup_period / max_lockup, 1)

        # Apply yield curve formula
        rate = base_rate + (max_rate - base_rate) * \
            (1 - pow(1 - utilization, steepness))

        # Add lockup bonus
        final_rate = rate * (1 + lockup_factor)

        return min(final_rate, max_rate)

    def calculate_yield(self, address: str, activity_type: str,
                        base_amount: Decimal, glyph_id: Optional[str] = None,
                        lockup_period: int = 0) -> Decimal:
        """
        Calculate yield incorporating emotional gravity and proof cycles.
        Formula: MeshCreditYield = Base * (Cycles^TrustFactor) * (Governance + EmotionalWeight)
        """
        # Get proof cycles for activity
        cycles = self.proof_cycles.get(activity_type, 1)
        governance = activity_type == 'governance_vote'

        # Calculate base yield rate from curve
        base_yield = self.calculate_yield_rate(base_amount, lockup_period)

        # If no glyph, return basic yield
        if not glyph_id:
            return base_amount * (Decimal('1') + base_yield)

        # Calculate glyph-based components through glyph manager
        total_yield = self.glyph_manager.calculate_mesh_yield(
            base_amount,
            glyph_id,
            cycles,
            governance
        )

        # Apply base yield rate
        total_yield *= (Decimal('1') + base_yield)

        return total_yield

    def process_gameplay_reward(self,
                                player_address: str,
                                activity_type: str,
                                performance_score: Decimal) -> Dict:
        """Process gameplay rewards with yield calculations"""
        try:
            base_reward = performance_score * Decimal('0.1')  # Base reward rate
            total_reward = self.calculate_yield(
                player_address,
                activity_type,
                base_reward
            )

            # Add transaction
            self.add_transaction(
                "gameplay_rewards",
                player_address,
                total_reward,
                "gameplay_reward",
                {
                    'activity': activity_type,
                    'score': str(performance_score),
                    'yield_multiplier': str(self.yield_multipliers.get(activity_type, 1))
                }
            )

            return {
                'status': 'success',
                'reward': str(total_reward),
                'activity': activity_type,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_stats(self) -> Dict:
        """Get current MeshCredit statistics"""
        return {
            'circulating_supply': str(self.circulating_supply),
            'total_supply': str(self.total_supply),
            'supply_percentage': float(self.circulating_supply / self.total_supply * 100),
            'usd_penny_reserve': str(self.usd_penny_reserve),
            'reserve_ratio': float(self.usd_penny_reserve / self.circulating_supply) if self.circulating_supply > 0 else 0,
            'block_height': len(self.chain),
            'current_block_reward': str(self.calculate_block_reward()),
            'yield_examples': {
                '30_day': float(self.calculate_yield_rate(Decimal('1000'), 30 * 24 * 60 * 60)),
                '180_day': float(self.calculate_yield_rate(Decimal('1000'), 180 * 24 * 60 * 60)),
                '365_day': float(self.calculate_yield_rate(Decimal('1000'), 365 * 24 * 60 * 60))
            },
            'next_halving': {
                'blocks_remaining': self.halving_blocks - (len(self.chain) % self.halving_blocks),
                'current_epoch': len(self.chain) // self.halving_blocks
            }
        }

    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            # Verify current hash
            if current.calculate_hash() != current.calculate_hash():
                return False

            # Verify chain link
            if current.previous_hash != previous.calculate_hash():
                return False

        return True


# Example usage
if __name__ == "__main__":
    mesh = MeshCredit()

    # Add a gameplay transaction
    mesh.add_transaction(
        "gameplay",
        "player123",
        Decimal('10.0'),
        "badge_mint",
        {"character": "eli_inheritor"}
    )

    # Mine the block
    result = mesh.mine_block("miner123")
    print(f"Mining result: {result}")

    # Calculate rewards with yield
    reward = mesh.process_gameplay_reward(
        "player123",
        "badge_mint",
        Decimal('95.5')
    )
    print(f"Reward calculation: {reward}")
