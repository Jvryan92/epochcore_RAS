#!/usr/bin/env python3
import os
import json
import hashlib
import datetime as dt
import uuid
import hmac
from typing import Dict, List, Optional, Set


class OptimizationMesh:
    """
    Autonomous optimization mesh for technical system improvements.
    Uses cryptographic proofs to verify and track system changes.
    """

    def __init__(self, cas_path: str):
        self.cas_path = cas_path
        self.mesh_key = os.urandom(32)
        self.ledger_path = os.path.join(cas_path, "optimization_ledger.jsonl")
        os.makedirs(cas_path, exist_ok=True)

    def _ts(self) -> str:
        """Generate UTC timestamp."""
        return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _hash(self, data: bytes) -> str:
        """Generate SHA-256 hash."""
        return hashlib.sha256(data).hexdigest()

    def _sign(self, data: bytes) -> str:
        """Generate HMAC signature."""
        return hmac.new(self.mesh_key, data, hashlib.sha256).hexdigest()

    def store_improvement(
        self, component: str, metrics: Dict[str, Dict[str, float]], changes: List[Dict]
    ) -> str:
        """
        Store a system improvement with cryptographic proof.

        Args:
            component: System component being improved
            metrics: Performance metrics before/after
            changes: List of specific changes made

        Returns:
            Merkle root of improvement proof
        """
        improvement = {
            "id": f"OPT-{uuid.uuid4().hex[:8]}",
            "timestamp": self._ts(),
            "component": component,
            "metrics": metrics,
            "changes": changes,
        }

        # Create proof chain
        proof_items = []

        # Hash component state
        comp_hash = self._hash(json.dumps(component).encode())
        proof_items.append(comp_hash)

        # Hash metrics
        metrics_hash = self._hash(json.dumps(metrics).encode())
        proof_items.append(metrics_hash)

        # Hash each change
        for change in changes:
            change_hash = self._hash(json.dumps(change).encode())
            proof_items.append(change_hash)

        # Calculate merkle root
        merkle_root = self._calculate_merkle_root(proof_items)
        improvement["merkle_root"] = merkle_root

        # Sign final improvement
        data = json.dumps(improvement, sort_keys=True).encode()
        improvement["signature"] = self._sign(data)

        # Store in CAS
        self._store_cas(data)

        # Update ledger
        self._append_ledger(improvement)

        return merkle_root

    def _calculate_merkle_root(self, items: List[str]) -> str:
        """Calculate merkle root of proof items."""
        if not items:
            return self._hash(b"")

        nodes = items
        while len(nodes) > 1:
            pairs = [
                (nodes[i], nodes[i + 1] if i + 1 < len(nodes) else nodes[i])
                for i in range(0, len(nodes), 2)
            ]
            nodes = [self._hash(bytes.fromhex(a) + bytes.fromhex(b)) for a, b in pairs]
        return nodes[0]

    def _store_cas(self, data: bytes) -> None:
        """Store data in content-addressable storage."""
        h = self._hash(data)
        path = os.path.join(self.cas_path, f"{h}.bin")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)

    def _append_ledger(self, entry: Dict) -> None:
        """Append entry to optimization ledger."""
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")


class SystemOptimizer:
    """
    Autonomous system optimization engine that tracks improvements
    with cryptographic proofs.
    """

    def __init__(self, cas_path: str):
        self.mesh = OptimizationMesh(cas_path)
        self.components: Set[str] = set()
        self.improvement_roots: List[str] = []

    def register_component(self, name: str) -> None:
        """Register a system component for optimization."""
        self.components.add(name)

    def improve_component(
        self, name: str, metrics: Dict[str, Dict[str, float]], changes: List[Dict]
    ) -> Optional[str]:
        """
        Record a component improvement with cryptographic proof.

        Args:
            name: Component name
            metrics: Performance metrics showing improvement
            changes: List of changes made

        Returns:
            Merkle root of improvement proof
        """
        if name not in self.components:
            return None

        root = self.mesh.store_improvement(name, metrics, changes)
        self.improvement_roots.append(root)
        return root

    def get_system_root(self) -> str:
        """Get merkle root of all system improvements."""
        return self.mesh._calculate_merkle_root(self.improvement_roots)
