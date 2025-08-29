"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MeshGlyph:
    """Represents a trust-weighted glyph in the MeshCredit system"""
    glyph_id: str
    trust_weight: float  # 0.0 to 1.0
    emotional_resonance: float  # -1.0 to 1.0
    founder_status: bool


@dataclass
class MeshBlock:
    """Represents a block in the MeshCredit blockchain"""
    index: int
    timestamp: float
    transactions: List[Dict]
    previous_hash: str
    proof_gravity: float  # Emotional gravity score
    glyphs: List[MeshGlyph]
    hash: Optional[str] = None


class MeshCredit:
    """
    MeshCredit cryptocurrency implementation with:
    - Capped supply (21M max)
    - Penny backing
    - Glyph-based trust weighting
    - Emotional gravity in proof cycles
    """

    def __init__(self):
        self.chain: List[MeshBlock] = []
        self.pending_transactions: List[Dict] = []
        self.total_supply = 21_000_000  # Maximum supply cap
        self.current_supply = 0
        self.backing_pennies = 0  # Tracks penny backing
        self.min_gravity = 0.3  # Minimum emotional gravity required

        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Creates the genesis block with founder glyphs"""
        founder_glyphs = [
            MeshGlyph("FOUNDER_1", 1.0, 0.8, True),
            MeshGlyph("FOUNDER_2", 1.0, 0.7, True),
            MeshGlyph("FOUNDER_3", 1.0, 0.9, True)
        ]

        genesis_block = MeshBlock(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0",
            proof_gravity=1.0,
            glyphs=founder_glyphs
        )

        # Set genesis block hash
        genesis_block.hash = self.hash_block(genesis_block)
        self.chain.append(genesis_block)

    def hash_block(self, block: MeshBlock) -> str:
        """Creates SHA-256 hash of a block"""
        # Convert block to string and encode
        block_string = (
            f"{block.index}{block.timestamp}"
            f"{block.transactions}{block.previous_hash}"
            f"{block.proof_gravity}"
            f"{[g.glyph_id for g in block.glyphs]}"
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        """
        Add a new transaction to pending transactions.
        Returns False if it would exceed supply cap.
        """
        # Special case for genesis
        if sender == "GENESIS":
            print(f"\nProcessing Genesis Transaction:")
            print(f"Amount: {amount:,} MESH")
            print(f"Recipient: {recipient}")

            self.pending_transactions.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time.time()
            })

            # Mine genesis transaction immediately
            genesis_glyph = MeshGlyph(
                glyph_id="GENESIS_MINER",
                trust_weight=1.0,
                emotional_resonance=1.0,
                founder_status=True
            )

            block = self.mine_block(genesis_glyph)
            if block:
                print("Genesis block mined successfully")
                print(f"Block hash: {block.hash}")
                self.current_supply += amount
                return True
            else:
                print("Genesis block mining failed!")
                return False

        # Normal transaction
        if self.current_supply + amount > self.total_supply:
            return False

        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': time.time()
        })

        # Auto-mine transaction
        auto_glyph = MeshGlyph(
            glyph_id=f"AUTO_MINER_{int(time.time())}",
            trust_weight=0.8,
            emotional_resonance=0.8,
            founder_status=False
        )

        return self.mine_block(auto_glyph) is not None

    def mine_block(self, miner_glyph: MeshGlyph) -> Optional[MeshBlock]:
        """
        Mine a new block with emotional gravity proof.
        Returns None if gravity threshold not met.
        """
        if not self.pending_transactions:
            return None

        # Calculate proof gravity from glyph
        gravity = miner_glyph.trust_weight * miner_glyph.emotional_resonance

        if gravity < self.min_gravity:
            return None

        last_block = self.chain[-1]

        new_block = MeshBlock(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions,
            previous_hash=last_block.hash,
            proof_gravity=gravity,
            glyphs=[miner_glyph]
        )

        # Calculate new block hash
        new_block.hash = self.hash_block(new_block)

        # Update state
        self.chain.append(new_block)
        self.pending_transactions = []
        self.current_supply += sum(t['amount'] for t in new_block.transactions)

        return new_block

    def get_balance(self, wallet_id: str) -> float:
        """Get balance for a wallet"""
        balance = 0

        for block in self.chain:
            for tx in block.transactions:
                if tx['recipient'] == wallet_id:
                    balance += tx['amount']
                    print(f"Credit: +{tx['amount']:,} from {tx['sender']}")
                if tx['sender'] == wallet_id:
                    balance -= tx['amount']
                    print(f"Debit: -{tx['amount']:,} to {tx['recipient']}")

        return balance

    def verify_chain(self) -> bool:
        """Verify integrity of the entire chain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            # Verify hash
            if current.hash != self.hash_block(current):
                return False

            # Verify chain linkage
            if current.previous_hash != previous.hash:
                return False

            # Verify proof gravity
            if current.proof_gravity < self.min_gravity:
                return False

        return True

    def back_with_pennies(self, penny_amount: int) -> None:
        """Add penny backing to increase stability"""
        self.backing_pennies += penny_amount
