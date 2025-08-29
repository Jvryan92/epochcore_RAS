#!/usr/bin/env python3
import os
import json
import hashlib
import hmac
import datetime as dt
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Pattern:
    id: str
    mesh_ids: List[str]
    sequence: List[Dict]
    confidence: float
    frequency: int
    timestamp: str


class PatternRecognizer:
    """Cross-mesh pattern recognition system with cryptographic verification."""

    def __init__(self, cas_path: str, mesh_key: bytes):
        self.cas_path = cas_path
        self.mesh_key = mesh_key
        self.patterns: Dict[str, Pattern] = {}
        self.sequence_cache: Dict[str, List[Dict]] = defaultdict(list)
        self.merkle_roots: List[str] = []

    def analyze_segment(self, mesh_id: str, segment: Dict) -> List[str]:
        """
        Analyze a mesh segment for patterns.
        Returns list of pattern IDs found.
        """
        # Extract action sequence
        actions = segment.get("actions", [])
        sequence = [
            {"action": a["action"], "agent": a["agent"], "status": a["status"]}
            for a in actions
            if a["status"] == "completed"
        ]

        # Add to sequence cache
        self.sequence_cache[mesh_id].extend(sequence)

        # Look for patterns
        found_patterns = []
        for pattern in self.patterns.values():
            if self._match_sequence(sequence, pattern.sequence):
                found_patterns.append(pattern.id)
                pattern.frequency += 1

        return found_patterns

    def _match_sequence(self, sequence: List[Dict], pattern: List[Dict]) -> bool:
        """Check if sequence matches pattern."""
        if len(sequence) < len(pattern):
            return False

        # Sliding window match
        for i in range(len(sequence) - len(pattern) + 1):
            window = sequence[i : i + len(pattern)]
            if all(self._match_action(w, p) for w, p in zip(window, pattern)):
                return True
        return False

    def _match_action(self, action: Dict, pattern: Dict) -> bool:
        """Check if action matches pattern element."""
        return all(pattern.get(k) == v for k, v in action.items() if k in pattern)

    def discover_patterns(
        self, min_freq: int = 3, min_conf: float = 0.7
    ) -> List[Pattern]:
        """
        Discover new patterns across meshes.
        Returns list of new patterns found.
        """
        new_patterns = []

        # For each mesh combination
        mesh_ids = list(self.sequence_cache.keys())
        for i, mesh_id in enumerate(mesh_ids):
            base_seq = self.sequence_cache[mesh_id]

            # Look for similar sequences in other meshes
            for other_id in mesh_ids[i + 1 :]:
                other_seq = self.sequence_cache[other_id]

                # Find common subsequences
                common = self._find_common_sequences(base_seq, other_seq)

                for seq, freq, conf in common:
                    if freq >= min_freq and conf >= min_conf:
                        # Create new pattern
                        pattern = Pattern(
                            id=f"PAT-{hashlib.sha256(str(seq).encode()).hexdigest()[:8]}",
                            mesh_ids=[mesh_id, other_id],
                            sequence=seq,
                            confidence=conf,
                            frequency=freq,
                            timestamp=dt.datetime.now(dt.UTC).strftime(
                                "%Y-%m-%dT%H:%M:%SZ"
                            ),
                        )

                        self.patterns[pattern.id] = pattern
                        new_patterns.append(pattern)

                        # Create cryptographic proof
                        self._create_pattern_proof(pattern)

        return new_patterns

    def _find_common_sequences(
        self, seq1: List[Dict], seq2: List[Dict]
    ) -> List[Tuple[List[Dict], int, float]]:
        """Find common subsequences between two sequences."""
        common = []

        # Use sliding windows of different sizes
        for size in range(2, min(len(seq1), len(seq2)) + 1):
            windows1 = [seq1[i : i + size] for i in range(len(seq1) - size + 1)]
            windows2 = [seq2[i : i + size] for i in range(len(seq2) - size + 1)]

            for w1 in windows1:
                matches = sum(1 for w2 in windows2 if self._match_sequence(w2, w1))
                if matches > 0:
                    confidence = matches / len(windows2)
                    common.append((w1, matches, confidence))

        return common

    def _create_pattern_proof(self, pattern: Pattern) -> str:
        """Create cryptographic proof of pattern."""
        # Create proof document
        proof = {
            "pattern_id": pattern.id,
            "mesh_ids": pattern.mesh_ids,
            "sequence_hash": hashlib.sha256(str(pattern.sequence).encode()).hexdigest(),
            "confidence": pattern.confidence,
            "frequency": pattern.frequency,
            "timestamp": pattern.timestamp,
        }

        # Sign proof
        proof_bytes = json.dumps(proof, sort_keys=True).encode()
        proof["signature"] = hmac.new(
            self.mesh_key, proof_bytes, hashlib.sha256
        ).hexdigest()

        # Store proof
        proof_hash = hashlib.sha256(proof_bytes).hexdigest()
        path = os.path.join(self.cas_path, f"{proof_hash}.proof")
        with open(path, "w") as f:
            json.dump(proof, f, indent=2)

        self.merkle_roots.append(proof_hash)
        return proof_hash

    def get_proof_root(self) -> str:
        """Get merkle root of all pattern proofs."""
        if not self.merkle_roots:
            return hashlib.sha256(b"").hexdigest()

        nodes = self.merkle_roots
        while len(nodes) > 1:
            pairs = [
                (nodes[i], nodes[i + 1] if i + 1 < len(nodes) else nodes[i])
                for i in range(0, len(nodes), 2)
            ]
            nodes = [
                hashlib.sha256(bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()
                for a, b in pairs
            ]
        return nodes[0]
