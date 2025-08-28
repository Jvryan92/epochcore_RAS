"""Ledger Agent for secure distributed coordination."""

import asyncio
import hashlib
import hmac
import json
import os
import statistics
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.async_base_agent import AsyncBaseAgent
from ..core.error_handling import safe_operation, with_retry, RetryableError
from ..core.monitoring import AgentMonitor


class LedgerAgent(AsyncBaseAgent):
    """Agent for managing secure distributed ledger operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Ledger Agent.

        Args:
            config: Agent configuration
        """
        super().__init__("ledger_agent", config)
        self.monitor = AgentMonitor()
        self.base_dir = Path(self.config.get("base_dir", "./ledger"))
        self.cas_dir = self.base_dir / "cas"
        self.segments = self.config.get("segments", 100)
        self.cycles_per_segment = self.config.get("cycles_per_segment", 100)
        self.slo_ms = self.config.get("slo_ms", 300)
        self.budget = float(self.config.get("budget", 5000))
        self.power_index = self.config.get("power_index", 16)
        
        # Ensure directories exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.cas_dir.mkdir(parents=True, exist_ok=True)

    @safe_operation("ledger_init")
    async def initialize_ledger(self) -> Dict[str, Any]:
        """Initialize the ledger system.

        Returns:
            Initialization status
        """
        # Generate root key using enhanced security
        self.root_key = await self._generate_root_key()
        
        # Initialize key hierarchy
        self.keys = await self._initialize_key_hierarchy()
        
        # Create initial ledger state
        state = {
            "ts": self._get_timestamp(),
            "root": self._hash_string(f"genesis:drip:{self.config.get('seed', 'TrueNorth')}"),
            "last": "genesis",
            "segments": []
        }
        
        await self._write_json(self.base_dir / "drip_chain_state.json", state)
        return {"status": "initialized", "state": state}

    @safe_operation(max_retries=3)
    @with_retry(max_retries=3)
    async def process_segment(self, segment_num: int) -> Dict[str, Any]:
        """Process a single ledger segment.

        Args:
            segment_num: Segment number to process

        Returns:
            Segment processing results
        """
        self.monitor.start_operation(f"segment_{segment_num}")
        
        try:
            # Generate segment keys
            seg_keys = await self._derive_segment_keys(segment_num)
            
            # Process cycles
            cycles = await self._process_cycles(segment_num)
            
            # Calculate Merkle root
            merkle_root = await self._calculate_merkle_root(cycles)
            
            # Create segment capsule
            capsule = await self._create_segment_capsule(
                segment_num, cycles, merkle_root, seg_keys
            )
            
            # Update ledger
            await self._update_ledger(capsule)
            
            self.monitor.end_operation(f"segment_{segment_num}")
            return capsule
            
        except Exception as e:
            self.logger.error(f"Segment {segment_num} processing failed: {str(e)}")
            raise RetryableError(f"Segment processing failed: {str(e)}")

    async def _derive_segment_keys(self, segment_num: int) -> Dict[str, bytes]:
        """Derive cryptographic keys for a segment.

        Args:
            segment_num: Segment number

        Returns:
            Dictionary of derived keys
        """
        seed = self.config.get("seed", "TrueNorth")
        prk = self._hkdf_extract(
            self._hash_string(f"SEG:{segment_num}:{seed}").encode(),
            self.root_key
        )
        
        return {
            "segment": self._hkdf_expand(prk, b"DRIP-SEG"),
            "ledger": self._hkdf_expand(prk, b"LEDGER")
        }

    @safe_operation("merkle_calculation")
    async def _calculate_merkle_root(self, items: List[str]) -> str:
        """Calculate Merkle tree root.

        Args:
            items: List of items to include in Merkle tree

        Returns:
            Merkle root hash
        """
        if not items:
            return hashlib.sha256(b"").hexdigest()
            
        nodes = [bytes.fromhex(x) for x in items]
        
        while len(nodes) > 1:
            new_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
                new_level.append(hashlib.sha256(left + right).digest())
            nodes = new_level
            
        return nodes[0].hex()

    def _get_timestamp(self) -> str:
        """Get ISO format timestamp.

        Returns:
            Current UTC timestamp
        """
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _hash_string(self, s: str) -> str:
        """Create SHA-256 hash of string.

        Args:
            s: String to hash

        Returns:
            Hex string of hash
        """
        return hashlib.sha256(s.encode()).hexdigest()

    def _hkdf_extract(self, salt: bytes, input_key: bytes) -> bytes:
        """HKDF extraction function.

        Args:
            salt: Salt value
            input_key: Input key material

        Returns:
            Extracted key material
        """
        return hmac.new(salt, input_key, hashlib.sha256).digest()

    def _hkdf_expand(self, prk: bytes, info: bytes, length: int = 32) -> bytes:
        """HKDF expansion function.

        Args:
            prk: Pseudorandom key
            info: Context info
            length: Output length

        Returns:
            Expanded key material
        """
        output = b""
        T = b""
        i = 1
        
        while len(output) < length:
            T = hmac.new(prk, T + info + bytes([i]), hashlib.sha256).digest()
            output += T
            i += 1
            
        return output[:length]

    async def _write_json(self, path: Path, data: Any):
        """Write JSON data to file atomically.

        Args:
            path: Output path
            data: Data to write
        """
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        os.replace(temp_path, path)
