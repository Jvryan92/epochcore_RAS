import datetime as dt
import hashlib
import hmac
import json
import os
from typing import Dict, List, Optional, Set, Tuple

from .trigger_mint import TriggerMint

class MeshTriggerProcessor:
    """
    Processes triggers within the cryptographic mesh network, integrating with the 
    existing CAS and ledger infrastructure.
    """
    
    def __init__(self, mesh_id: str, cas_path: str, mesh_key: bytes):
        self.mesh_id = mesh_id
        self.minter = TriggerMint(cas_path, mesh_key)
        self.ledger_path = os.path.join(cas_path, f"{mesh_id}_trigger_ledger.jsonl")
        self.merkle_roots: List[str] = []
        
    def process_capsule(self, capsule_data: Dict, 
                       triggers: List[str]) -> Tuple[str, List[Dict]]:
        """
        Process a capsule with triggers and integrate into mesh state.
        
        Args:
            capsule_data: The original capsule data
            triggers: List of trigger strings to process
            
        Returns:
            Tuple of (merkle_root, minted_records)
        """
        # Mint new triggers
        minted = self.minter.mint(triggers)
        
        # Create trigger capsule
        capsule = {
            "id": f"TRIG-{self.mesh_id}-{dt.datetime.now(dt.UTC).strftime('%Y%m%d%H%M%S')}",
            "timestamp": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mesh_id": self.mesh_id,
            "source_capsule": capsule_data.get("id"),
            "triggers": triggers,
            "minted": minted
        }
        
        # Sign capsule
        capsule["hash"] = self._hash_obj(capsule)
        capsule["signature"] = hmac.new(
            self.minter.mesh_key,
            json.dumps(capsule, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store in CAS
        self._store_capsule(capsule)
        
        # Update ledger
        self._append_ledger(capsule)
        
        # Calculate merkle root
        merkle_root = self.minter._calculate_merkle_root(
            [r.get("hash", "") for r in minted]
        )
        self.merkle_roots.append(merkle_root)
        
        return merkle_root, minted
        
    def _hash_obj(self, obj: Dict) -> str:
        """Generate stable hash of object."""
        s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(s.encode()).hexdigest()
        
    def _store_capsule(self, capsule: Dict) -> None:
        """Store capsule in CAS."""
        h = self._hash_obj(capsule)
        path = os.path.join(self.minter.cas_path, f"{h}.json")
        with open(path, "w") as f:
            json.dump(capsule, f, indent=2)
            
    def _append_ledger(self, entry: Dict) -> None:
        """Append entry to trigger ledger."""
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_merkle_root(self) -> str:
        """Get merkle root of all trigger operations."""
        return self.minter._calculate_merkle_root(self.merkle_roots)

class TriggerAgent:
    """
    Agent specialized for handling trigger operations within the mesh.
    """
    
    def __init__(self, agent_id: str, cas_path: str, mesh_key: bytes):
        self.agent_id = agent_id
        self.cas_path = cas_path
        self.mesh_key = mesh_key
        self.processors: Dict[str, MeshTriggerProcessor] = {}
        
    def handle_capsule(self, mesh_id: str, capsule: Dict) -> Optional[str]:
        """
        Process triggers in a capsule for a specific mesh.
        
        Returns merkle root if triggers were processed.
        """
        # Extract triggers from capsule
        triggers = self._extract_triggers(capsule)
        if not triggers:
            return None
            
        # Get/create processor for mesh
        if mesh_id not in self.processors:
            self.processors[mesh_id] = MeshTriggerProcessor(
                mesh_id, self.cas_path, self.mesh_key
            )
        
        # Process triggers
        merkle_root, _ = self.processors[mesh_id].process_capsule(
            capsule, triggers
        )
        
        return merkle_root
        
    def _extract_triggers(self, capsule: Dict) -> List[str]:
        """Extract triggers from capsule data."""
        # Example trigger extraction logic
        actions = capsule.get("actions", [])
        triggers = set()
        
        for action in actions:
            if action["status"] == "completed":
                # Map actions to potential triggers
                if action["action"] == "atomize":
                    triggers.add("VELOCITY")
                elif action["action"] in ("diffuse", "sync"):
                    triggers.add("CONSTELLATION")
                elif action["action"] == "verify":
                    triggers.add("LEDGERLOCK")
                elif action["action"] == "measure":
                    triggers.add("AMPLIFY")
                    
        return list(triggers)
