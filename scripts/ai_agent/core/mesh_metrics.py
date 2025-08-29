"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
import json
import datetime as dt
from typing import Dict, List, Optional, Set, Any

class MeshMetrics:
    """
    Collects and analyzes mesh performance metrics.
    """
    
    def __init__(self):
        self.latency_samples: List[float] = []
        self.throughput_samples: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.pattern_hits: Dict[str, int] = {}
        self.topology_changes: List[Dict] = []
        
    def record_latency(self, latency_ms: float) -> None:
        """Record a latency measurement."""
        self.latency_samples.append(latency_ms)
        
        # Keep reasonable sample size
        if len(self.latency_samples) > 1000:
            self.latency_samples = self.latency_samples[-1000:]
            
    def record_throughput(self, ops_per_sec: float) -> None:
        """Record a throughput measurement."""
        self.throughput_samples.append(ops_per_sec)
        
        # Keep reasonable sample size
        if len(self.throughput_samples) > 1000:
            self.throughput_samples = self.throughput_samples[-1000:]
            
    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self.error_counts[error_type] = \
            self.error_counts.get(error_type, 0) + 1
            
    def record_pattern_hit(self, pattern_id: str) -> None:
        """Record a pattern match."""
        self.pattern_hits[pattern_id] = \
            self.pattern_hits.get(pattern_id, 0) + 1
            
    def record_topology_change(self,
                             old_config: Dict,
                             new_config: Dict,
                             reason: str) -> None:
        """Record a topology configuration change."""
        self.topology_changes.append({
            'timestamp': dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'old_config': old_config,
            'new_config': new_config,
            'reason': reason
        })
        
    def get_latency_stats(self) -> Dict[str, float]:
        """Get summary statistics for latency."""
        if not self.latency_samples:
            return {}
            
        samples = sorted(self.latency_samples)
        return {
            'min': samples[0],
            'max': samples[-1],
            'avg': sum(samples) / len(samples),
            'p50': samples[len(samples)//2],
            'p90': samples[int(len(samples)*0.9)],
            'p99': samples[int(len(samples)*0.99)]
        }
        
    def get_throughput_stats(self) -> Dict[str, float]:
        """Get summary statistics for throughput."""
        if not self.throughput_samples:
            return {}
            
        samples = sorted(self.throughput_samples)
        return {
            'min': samples[0],
            'max': samples[-1],
            'avg': sum(samples) / len(samples),
            'p50': samples[len(samples)//2],
            'p90': samples[int(len(samples)*0.9)],
            'p99': samples[int(len(samples)*0.99)]
        }
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_counts:
            return {}
            
        total = sum(self.error_counts.values())
        return {
            'total': total,
            'by_type': self.error_counts,
            'rates': {
                err_type: count/total
                for err_type, count in self.error_counts.items()
            }
        }
        
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get pattern match statistics."""
        if not self.pattern_hits:
            return {}
            
        total = sum(self.pattern_hits.values())
        return {
            'total': total,
            'by_pattern': self.pattern_hits,
            'rates': {
                pattern: count/total
                for pattern, count in self.pattern_hits.items()
            }
        }
        
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get topology change statistics."""
        if not self.topology_changes:
            return {}
            
        # Group by reason
        by_reason: Dict[str, int] = {}
        for change in self.topology_changes:
            reason = change['reason']
            by_reason[reason] = by_reason.get(reason, 0) + 1
            
        return {
            'total_changes': len(self.topology_changes),
            'by_reason': by_reason,
            'recent': self.topology_changes[-5:]  # Last 5 changes
        }
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            'timestamp': dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'latency': self.get_latency_stats(),
            'throughput': self.get_throughput_stats(),
            'errors': self.get_error_summary(),
            'patterns': self.get_pattern_summary(),
            'topology': self.get_topology_summary()
        }
        
    def reset(self) -> None:
        """Reset all metrics."""
        self.latency_samples = []
        self.throughput_samples = []
        self.error_counts = {}
        self.pattern_hits = {}
        self.topology_changes = []
