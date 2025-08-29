"""
Blockchain-based Protection System for EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
"""

import hashlib
import json
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProtectionBlock:
    """A block in the protection blockchain."""

    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate block hash with proof of work."""
        while True:
            block_content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
            calculated_hash = hashlib.sha256(block_content.encode()).hexdigest()
            if calculated_hash.startswith("000"):  # Proof of work
                return calculated_hash
            self.nonce += 1


class ProtectionChain:
    """Blockchain-based protection system."""

    def __init__(self, chain_dir: Optional[str] = None):
        self.chain: List[ProtectionBlock] = []
        self.chain_dir = Path(chain_dir or ".protection_chain")
        self.chain_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with genesis block
        if not self.chain:
            self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the genesis block."""
        genesis_data = {
            "type": "genesis",
            "creator": "John Ryan",
            "business": "EpochCore Business",
            "timestamp": datetime.now().isoformat(),
            "license": "Proprietary - All Rights Reserved"
        }
        genesis_block = ProtectionBlock(
            0, datetime.now().isoformat(), genesis_data, "0")
        self.chain.append(genesis_block)
        self._save_block(genesis_block)

    def add_content_block(self, content_data: Dict) -> str:
        """Add a new block for content protection."""
        protection_data = {
            "type": "content_protection",
            "timestamp": datetime.now().isoformat(),
            "content_hash": hashlib.sha256(
                json.dumps(content_data, sort_keys=True).encode()
            ).hexdigest(),
            "copyright": {
                "owner": "John Ryan",
                "business": "EpochCore Business",
                "year": "2024",
                "rights": "All Rights Reserved"
            },
            "protection_level": "maximum",
            "verification_required": True
        }

        new_block = ProtectionBlock(
            len(self.chain),
            datetime.now().isoformat(),
            protection_data,
            self.chain[-1].hash
        )

        self.chain.append(new_block)
        self._save_block(new_block)
        return new_block.hash

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire chain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            # Verify block hash
            if current.hash != current.calculate_hash():
                return False

            # Verify chain link
            if current.previous_hash != previous.hash:
                return False

        return True

    def _save_block(self, block: ProtectionBlock):
        """Save block to persistent storage."""
        block_file = self.chain_dir / f"block_{block.index}.json"
        block_data = {
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "nonce": block.nonce
        }
        block_file.write_text(json.dumps(block_data, indent=2))

    def get_protection_status(self) -> Dict:
        """Get current protection chain status."""
        return {
            "chain_length": len(self.chain),
            "latest_block": self.chain[-1].hash,
            "timestamp": datetime.now().isoformat(),
            "integrity_verified": self.verify_chain(),
            "total_protected_content": len(self.chain) - 1  # Exclude genesis
        }
