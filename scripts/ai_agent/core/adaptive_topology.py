"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
import os
import json
import hashlib
import hmac
import datetime as dt
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class TopologyChange:
    id: str
    timestamp: str
    mesh_id: str
    old_config: Dict
    new_config: Dict
    metrics: Dict[str, float]
    proof_hash: str

class AdaptiveTopology:
    """
    Dynamically adjusts mesh topology based on performance metrics
    with cryptographic proof of changes.
    """
    
    def __init__(self, cas_path: str, mesh_key: bytes):
        self.cas_path = cas_path
        self.mesh_key = mesh_key
        self.changes: Dict[str, TopologyChange] = {}
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)
        self.merkle_roots: List[str] = []
        
    def record_performance(self, mesh_id: str, metrics: Dict[str, float]) -> None:
        """Record performance metrics for a mesh."""
        self.performance_history[mesh_id].append({
            'timestamp': dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'metrics': metrics
        })
        
    def analyze_topology(self, mesh_id: str, 
                        current_config: Dict,
                        threshold: float = 0.15) -> Optional[Dict]:
        """
        Analyze mesh performance and suggest topology changes.
        Returns new config if changes needed, None otherwise.
        """
        if mesh_id not in self.performance_history:
            return None
            
        history = self.performance_history[mesh_id]
        if len(history) < 5:  # Need minimum history
            return None
            
        # Calculate performance trends
        trends = self._calculate_trends(history)
        
        # Check if changes needed
        if self._needs_optimization(trends, threshold):
            return self._generate_new_config(
                current_config, 
                trends
            )
            
        return None
        
    def _calculate_trends(self, 
                         history: List[Dict]) -> Dict[str, float]:
        """Calculate performance trends from history."""
        trends = {}
        
        # Get metrics from most recent entry
        latest = history[-1]['metrics']
        
        # Calculate moving averages
        window = history[-5:]  # Last 5 entries
        averages = defaultdict(list)
        
        for entry in window:
            for metric, value in entry['metrics'].items():
                averages[metric].append(value)
                
        # Calculate trends vs moving average
        for metric, values in averages.items():
            avg = sum(values) / len(values)
            if avg != 0:
                trends[metric] = (latest[metric] - avg) / avg
            else:
                trends[metric] = 0
                
        return trends
        
    def _needs_optimization(self, 
                          trends: Dict[str, float],
                          threshold: float) -> bool:
        """Determine if topology optimization is needed."""
        # Check for significant degradation in any metric
        return any(abs(trend) > threshold 
                  for trend in trends.values())
        
    def _generate_new_config(self,
                            current: Dict,
                            trends: Dict[str, float]) -> Dict:
        """Generate optimized topology configuration."""
        new_config = current.copy()
        
        # Example optimization logic:
        if 'latency' in trends and trends['latency'] > 0:
            # Latency increasing - reduce path lengths
            if 'actions' in new_config:
                new_config['actions'] = sorted(
                    new_config['actions'],
                    key=lambda x: len(x)
                )
                
        if 'throughput' in trends and trends['throughput'] < 0:
            # Throughput decreasing - add parallel paths
            if 'agents' in new_config:
                # Add more agents to spread load
                agents = set(new_config['agents'])
                if len(agents) < 5:  # Max 5 agents
                    available = {'alpha','beta','gamma','delta','epsilon'}
                    new = available - agents
                    if new:
                        new_config['agents'] = list(
                            agents | {next(iter(new))}
                        )
                        
        return new_config
        
    def apply_changes(self, mesh_id: str,
                     old_config: Dict,
                     new_config: Dict,
                     metrics: Dict[str, float]) -> str:
        """
        Apply topology changes with cryptographic proof.
        Returns change ID.
        """
        # Create change record
        change_id = f"CHG-{hashlib.sha256(str(new_config).encode()).hexdigest()[:8]}"
        
        change = TopologyChange(
            id=change_id,
            timestamp=dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            mesh_id=mesh_id,
            old_config=old_config,
            new_config=new_config,
            metrics=metrics,
            proof_hash=''
        )
        
        # Create proof
        proof = {
            'change_id': change_id,
            'mesh_id': mesh_id,
            'timestamp': change.timestamp,
            'old_hash': hashlib.sha256(
                str(old_config).encode()
            ).hexdigest(),
            'new_hash': hashlib.sha256(
                str(new_config).encode()
            ).hexdigest(),
            'metrics': metrics
        }
        
        # Sign proof
        proof_bytes = json.dumps(proof, sort_keys=True).encode()
        proof['signature'] = hmac.new(
            self.mesh_key,
            proof_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Store proof
        proof_hash = hashlib.sha256(proof_bytes).hexdigest()
        path = os.path.join(self.cas_path, f"{proof_hash}.proof")
        with open(path, "w") as f:
            json.dump(proof, f, indent=2)
            
        # Update change record
        change.proof_hash = proof_hash
        self.changes[change_id] = change
        self.merkle_roots.append(proof_hash)
        
        return change_id
        
    def verify_change(self, change_id: str) -> bool:
        """Verify cryptographic proof of a topology change."""
        if change_id not in self.changes:
            return False
            
        change = self.changes[change_id]
        
        # Load proof
        path = os.path.join(self.cas_path, f"{change.proof_hash}.proof")
        if not os.path.exists(path):
            return False
            
        with open(path) as f:
            proof = json.load(f)
            
        # Verify signature
        proof_data = {k:v for k,v in proof.items() 
                     if k != 'signature'}
        proof_bytes = json.dumps(
            proof_data, 
            sort_keys=True
        ).encode()
        
        expected_sig = hmac.new(
            self.mesh_key,
            proof_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return proof['signature'] == expected_sig
        
    def get_proof_root(self) -> str:
        """Get merkle root of all topology change proofs."""
        if not self.merkle_roots:
            return hashlib.sha256(b"").hexdigest()
            
        nodes = self.merkle_roots
        while len(nodes) > 1:
            pairs = [
                (nodes[i], nodes[i+1] if i+1 < len(nodes) else nodes[i])
                for i in range(0, len(nodes), 2)
            ]
            nodes = [
                hashlib.sha256(
                    bytes.fromhex(a) + bytes.fromhex(b)
                ).hexdigest()
                for a, b in pairs
            ]
        return nodes[0]
