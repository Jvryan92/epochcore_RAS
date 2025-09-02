#!/usr/bin/env python3
"""
EpochCore RAS Capsule Metadata Management System

Manages asset integrity, storage optimization, and metadata management.
Includes recursive improvement hooks for autonomous storage optimization.
"""

import hashlib
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from recursive_improvement import ImprovementStrategy, SubsystemHook, get_framework


class CapsuleType(Enum):
    """Types of capsules in the system."""
    DATA = "data"
    MODEL = "model" 
    CODE = "code"
    CONFIG = "config"
    METADATA = "metadata"
    BACKUP = "backup"


class CapsuleStatus(Enum):
    """Status of a capsule."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


class Capsule:
    """Represents an asset capsule with metadata and integrity checks."""
    
    def __init__(self, capsule_id: str, name: str, capsule_type: CapsuleType,
                 content_hash: str, size_bytes: int = 0, metadata: Dict = None):
        self.id = capsule_id
        self.name = name
        self.type = capsule_type
        self.content_hash = content_hash
        self.size_bytes = size_bytes
        self.metadata = metadata or {}
        self.status = CapsuleStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.last_verified = datetime.now()
        self.access_count = 0
        self.verification_failures = 0
        self.storage_tier = "hot"  # hot, warm, cold, archived
        
    def to_dict(self) -> Dict:
        """Convert capsule to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "last_verified": self.last_verified.isoformat(),
            "access_count": self.access_count,
            "verification_failures": self.verification_failures,
            "storage_tier": self.storage_tier
        }
        
    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1
        
    def verify_integrity(self, actual_hash: str = None) -> bool:
        """Verify capsule integrity."""
        self.last_verified = datetime.now()
        
        # Simulate integrity check
        import random
        if random.random() < 0.95:  # 95% success rate
            return True
        else:
            self.verification_failures += 1
            if self.verification_failures > 3:
                self.status = CapsuleStatus.CORRUPTED
            return False


class CapsuleManager:
    """Manager for capsule storage and metadata."""
    
    def __init__(self):
        self.capsules = {}
        self.storage_stats = {
            "total_size": 0,
            "hot_storage": 0,
            "warm_storage": 0, 
            "cold_storage": 0,
            "archived_storage": 0
        }
        self.integrity_history = []
        
        # Initialize with sample capsules
        self._initialize_sample_capsules()
        
    def _initialize_sample_capsules(self):
        """Initialize with sample capsules for demonstration."""
        sample_capsules = [
            Capsule("cap_001", "User Dataset", CapsuleType.DATA, 
                   "a1b2c3d4", 1048576, {"format": "csv", "rows": 10000}),
            Capsule("cap_002", "ML Model v1.0", CapsuleType.MODEL,
                   "e5f6g7h8", 2097152, {"accuracy": 0.85, "version": "1.0"}),
            Capsule("cap_003", "Processing Script", CapsuleType.CODE,
                   "i9j0k1l2", 4096, {"language": "python", "version": "3.8"}),
            Capsule("cap_004", "System Config", CapsuleType.CONFIG,
                   "m3n4o5p6", 2048, {"environment": "production"}),
            Capsule("cap_005", "Audit Log", CapsuleType.METADATA,
                   "q7r8s9t0", 8192, {"period": "2024-01"}),
            Capsule("cap_006", "Model Backup v0.9", CapsuleType.BACKUP,
                   "u1v2w3x4", 1572864, {"backup_date": "2024-01-15"}),
            Capsule("cap_007", "Training Data", CapsuleType.DATA,
                   "y5z6a7b8", 5242880, {"samples": 50000}),
            Capsule("cap_008", "Config Backup", CapsuleType.BACKUP,
                   "c9d0e1f2", 1024, {"backup_type": "config"})
        ]
        
        # Simulate different access patterns and storage tiers
        sample_capsules[0].access_count = 150  # Frequently accessed
        sample_capsules[0].storage_tier = "hot"
        
        sample_capsules[1].access_count = 75
        sample_capsules[1].storage_tier = "warm"
        
        sample_capsules[2].access_count = 25
        sample_capsules[2].storage_tier = "warm"
        
        sample_capsules[5].access_count = 2  # Rarely accessed
        sample_capsules[5].storage_tier = "cold"
        sample_capsules[5].last_accessed = datetime.now() - timedelta(days=30)
        
        sample_capsules[7].access_count = 1
        sample_capsules[7].storage_tier = "archived"
        sample_capsules[7].status = CapsuleStatus.ARCHIVED
        sample_capsules[7].last_accessed = datetime.now() - timedelta(days=90)
        
        for capsule in sample_capsules:
            self.capsules[capsule.id] = capsule
            
        self._update_storage_stats()
        
    def _update_storage_stats(self):
        """Update storage statistics."""
        self.storage_stats = {
            "total_size": sum(c.size_bytes for c in self.capsules.values()),
            "hot_storage": sum(c.size_bytes for c in self.capsules.values() if c.storage_tier == "hot"),
            "warm_storage": sum(c.size_bytes for c in self.capsules.values() if c.storage_tier == "warm"),
            "cold_storage": sum(c.size_bytes for c in self.capsules.values() if c.storage_tier == "cold"),
            "archived_storage": sum(c.size_bytes for c in self.capsules.values() if c.storage_tier == "archived")
        }
        
    def add_capsule(self, capsule: Capsule) -> None:
        """Add a capsule to the system."""
        self.capsules[capsule.id] = capsule
        self._update_storage_stats()
        
    def get_capsule(self, capsule_id: str) -> Optional[Capsule]:
        """Get capsule by ID and update access statistics."""
        capsule = self.capsules.get(capsule_id)
        if capsule:
            capsule.update_access()
        return capsule
        
    def verify_all_capsules(self) -> Dict:
        """Verify integrity of all capsules."""
        verification_results = {
            "verified": 0,
            "failed": 0,
            "corrupted": 0,
            "details": []
        }
        
        for capsule in self.capsules.values():
            if capsule.verify_integrity():
                verification_results["verified"] += 1
            else:
                verification_results["failed"] += 1
                if capsule.status == CapsuleStatus.CORRUPTED:
                    verification_results["corrupted"] += 1
                    
            verification_results["details"].append({
                "capsule_id": capsule.id,
                "status": capsule.status.value,
                "verification_failures": capsule.verification_failures
            })
            
        self.integrity_history.append({
            "timestamp": datetime.now().isoformat(),
            "results": verification_results
        })
        
        return verification_results
        
    def optimize_storage_tiers(self) -> Dict:
        """Optimize storage tier assignments based on access patterns."""
        optimizations = []
        
        for capsule in self.capsules.values():
            old_tier = capsule.storage_tier
            days_since_access = (datetime.now() - capsule.last_accessed).days
            
            # Determine optimal tier based on access pattern
            if capsule.access_count > 100 and days_since_access < 7:
                optimal_tier = "hot"
            elif capsule.access_count > 20 or days_since_access < 30:
                optimal_tier = "warm"
            elif days_since_access < 90:
                optimal_tier = "cold"
            else:
                optimal_tier = "archived"
                if capsule.status == CapsuleStatus.ACTIVE:
                    capsule.status = CapsuleStatus.ARCHIVED
                    
            if optimal_tier != old_tier:
                capsule.storage_tier = optimal_tier
                optimizations.append({
                    "capsule_id": capsule.id,
                    "old_tier": old_tier,
                    "new_tier": optimal_tier,
                    "reason": f"Access count: {capsule.access_count}, Days since access: {days_since_access}"
                })
                
        self._update_storage_stats()
        
        return {
            "optimizations_made": len(optimizations),
            "details": optimizations
        }
        
    def get_system_state(self) -> Dict:
        """Get comprehensive capsule system state."""
        total_capsules = len(self.capsules)
        
        # Count by type
        type_counts = {}
        for capsule_type in CapsuleType:
            type_counts[capsule_type.value] = sum(1 for c in self.capsules.values() 
                                                 if c.type == capsule_type)
            
        # Count by status
        status_counts = {}
        for status in CapsuleStatus:
            status_counts[status.value] = sum(1 for c in self.capsules.values()
                                            if c.status == status)
            
        # Count by storage tier
        tier_counts = {}
        tier_sizes = {}
        for tier in ["hot", "warm", "cold", "archived"]:
            tier_capsules = [c for c in self.capsules.values() if c.storage_tier == tier]
            tier_counts[tier] = len(tier_capsules)
            tier_sizes[tier] = sum(c.size_bytes for c in tier_capsules)
            
        # Calculate integrity metrics
        recent_verifications = self.integrity_history[-10:] if self.integrity_history else []
        avg_integrity_rate = 0
        if recent_verifications:
            total_verified = sum(v["results"]["verified"] for v in recent_verifications)
            total_checked = sum(v["results"]["verified"] + v["results"]["failed"] 
                              for v in recent_verifications)
            avg_integrity_rate = total_verified / total_checked if total_checked > 0 else 1.0
            
        return {
            "total_capsules": total_capsules,
            "total_size_bytes": self.storage_stats["total_size"],
            "total_size_mb": round(self.storage_stats["total_size"] / 1048576, 2),
            "type_distribution": type_counts,
            "status_distribution": status_counts,
            "storage_tier_counts": tier_counts,
            "storage_tier_sizes": tier_sizes,
            "storage_stats": self.storage_stats,
            "integrity_rate": avg_integrity_rate,
            "corrupted_capsules": sum(1 for c in self.capsules.values() 
                                    if c.status == CapsuleStatus.CORRUPTED),
            "capsules": {cid: capsule.to_dict() for cid, capsule in self.capsules.items()},
            "timestamp": datetime.now().isoformat()
        }


class StorageOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing storage allocation and tier management."""
    
    def get_name(self) -> str:
        return "storage_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze storage usage and identify optimization opportunities."""
        opportunities = {
            "improvements_available": False,
            "tier_misallocations": [],
            "storage_inefficiencies": [],
            "optimization_potential": 0.0
        }
        
        total_size_mb = subsystem_state.get("total_size_mb", 0)
        tier_counts = subsystem_state.get("storage_tier_counts", {})
        capsules_data = subsystem_state.get("capsules", {})
        
        # Check for tier misallocations
        for capsule_id, capsule_data in capsules_data.items():
            access_count = capsule_data.get("access_count", 0)
            storage_tier = capsule_data.get("storage_tier", "warm")
            last_accessed = datetime.fromisoformat(capsule_data.get("last_accessed", datetime.now().isoformat()))
            days_since_access = (datetime.now() - last_accessed).days
            
            # Identify misallocated capsules
            if access_count > 50 and storage_tier in ["cold", "archived"]:
                opportunities["tier_misallocations"].append({
                    "capsule_id": capsule_id,
                    "current_tier": storage_tier,
                    "recommended_tier": "warm" if access_count < 100 else "hot",
                    "access_count": access_count,
                    "reason": "High access count but low-tier storage"
                })
                
            elif access_count < 5 and days_since_access > 60 and storage_tier in ["hot", "warm"]:
                opportunities["tier_misallocations"].append({
                    "capsule_id": capsule_id,
                    "current_tier": storage_tier,
                    "recommended_tier": "cold" if days_since_access < 90 else "archived",
                    "access_count": access_count,
                    "days_since_access": days_since_access,
                    "reason": "Low access count but high-tier storage"
                })
                
        # Check storage efficiency
        hot_storage_mb = subsystem_state.get("storage_stats", {}).get("hot_storage", 0) / 1048576
        if hot_storage_mb > 10:  # More than 10MB in hot storage
            opportunities["storage_inefficiencies"].append({
                "type": "hot_storage_overuse",
                "current_size_mb": hot_storage_mb,
                "recommended_max_mb": 10,
                "potential_savings_mb": hot_storage_mb - 10
            })
            
        if opportunities["tier_misallocations"] or opportunities["storage_inefficiencies"]:
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = (
                len(opportunities["tier_misallocations"]) * 0.1 +
                len(opportunities["storage_inefficiencies"]) * 0.15
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute storage optimization improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Fix tier misallocations
        for misallocation in opportunities.get("tier_misallocations", []):
            capsule_id = misallocation["capsule_id"]
            if capsule_id in improved_state["capsules"]:
                old_tier = improved_state["capsules"][capsule_id]["storage_tier"]
                new_tier = misallocation["recommended_tier"]
                improved_state["capsules"][capsule_id]["storage_tier"] = new_tier
                
                improvements_made.append({
                    "type": "tier_reallocation",
                    "capsule_id": capsule_id,
                    "old_tier": old_tier,
                    "new_tier": new_tier,
                    "reason": misallocation["reason"]
                })
                
        # Recalculate storage statistics
        if improvements_made:
            tier_sizes = {"hot": 0, "warm": 0, "cold": 0, "archived": 0}
            tier_counts = {"hot": 0, "warm": 0, "cold": 0, "archived": 0}
            
            for capsule_data in improved_state["capsules"].values():
                tier = capsule_data["storage_tier"]
                size_bytes = capsule_data["size_bytes"]
                tier_sizes[tier] += size_bytes
                tier_counts[tier] += 1
                
            improved_state["storage_tier_sizes"] = tier_sizes
            improved_state["storage_tier_counts"] = tier_counts
            improved_state["storage_stats"] = tier_sizes
            
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


class IntegrityEnhancementStrategy(ImprovementStrategy):
    """Strategy for enhancing capsule integrity and verification processes."""
    
    def get_name(self) -> str:
        return "integrity_enhancement"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze integrity status and identify improvement opportunities."""
        opportunities = {
            "improvements_available": False,
            "integrity_issues": [],
            "verification_gaps": [],
            "enhancement_potential": 0.0
        }
        
        integrity_rate = subsystem_state.get("integrity_rate", 1.0)
        corrupted_capsules = subsystem_state.get("corrupted_capsules", 0)
        capsules_data = subsystem_state.get("capsules", {})
        
        # Check for integrity issues
        if integrity_rate < 0.95:
            opportunities["integrity_issues"].append({
                "type": "low_integrity_rate",
                "current_rate": integrity_rate,
                "target_rate": 0.98,
                "improvement_needed": 0.98 - integrity_rate
            })
            
        if corrupted_capsules > 0:
            opportunities["integrity_issues"].append({
                "type": "corrupted_capsules",
                "count": corrupted_capsules,
                "action_required": "Recovery or replacement needed"
            })
            
        # Check for verification gaps
        for capsule_id, capsule_data in capsules_data.items():
            last_verified = datetime.fromisoformat(capsule_data.get("last_verified", datetime.now().isoformat()))
            days_since_verification = (datetime.now() - last_verified).days
            
            if days_since_verification > 30:  # Haven't verified in 30 days
                opportunities["verification_gaps"].append({
                    "capsule_id": capsule_id,
                    "days_since_verification": days_since_verification,
                    "verification_failures": capsule_data.get("verification_failures", 0)
                })
                
        if opportunities["integrity_issues"] or opportunities["verification_gaps"]:
            opportunities["improvements_available"] = True
            opportunities["enhancement_potential"] = (
                len(opportunities["integrity_issues"]) * 0.2 +
                min(len(opportunities["verification_gaps"]), 5) * 0.05  # Cap verification impact
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute integrity enhancement improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Improve verification processes
        verification_gaps = opportunities.get("verification_gaps", [])
        if verification_gaps:
            # Simulate running verification on stale capsules
            verified_count = 0
            for gap in verification_gaps[:5]:  # Process up to 5 capsules
                capsule_id = gap["capsule_id"]
                if capsule_id in improved_state["capsules"]:
                    # Update last verified timestamp
                    improved_state["capsules"][capsule_id]["last_verified"] = datetime.now().isoformat()
                    verified_count += 1
                    
            if verified_count > 0:
                improvements_made.append({
                    "type": "verification_update",
                    "capsules_verified": verified_count,
                    "description": "Updated verification timestamps for stale capsules"
                })
                
        # Improve integrity rate (simulate fixing issues)
        integrity_issues = opportunities.get("integrity_issues", [])
        for issue in integrity_issues:
            if issue["type"] == "low_integrity_rate":
                # Simulate integrity rate improvement
                old_rate = improved_state["integrity_rate"]
                improvement = min(0.05, issue["improvement_needed"])
                improved_state["integrity_rate"] = min(1.0, old_rate + improvement)
                
                improvements_made.append({
                    "type": "integrity_rate_improvement",
                    "old_rate": old_rate,
                    "new_rate": improved_state["integrity_rate"]
                })
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


# Global capsule manager instance
_capsule_manager = None


def get_capsule_manager() -> CapsuleManager:
    """Get or create the global capsule manager."""
    global _capsule_manager
    if _capsule_manager is None:
        _capsule_manager = CapsuleManager()
    return _capsule_manager


def initialize_capsule_management() -> SubsystemHook:
    """Initialize capsule management with recursive improvement hooks."""
    manager = get_capsule_manager()
    
    # Create improvement strategies
    strategies = [
        StorageOptimizationStrategy(),
        IntegrityEnhancementStrategy()
    ]
    
    # Create subsystem hook
    hook = SubsystemHook(
        name="capsules",
        get_state_func=manager.get_system_state,
        improvement_strategies=strategies
    )
    
    # Register with the framework
    framework = get_framework()
    framework.register_subsystem(hook)
    
    return hook


# Example usage functions
def improve_capsule_storage() -> Dict:
    """Manual trigger for capsule storage improvement."""
    framework = get_framework()
    return framework.run_manual_improvement("capsules")


def get_capsule_status() -> Dict:
    """Get current capsule system status."""
    manager = get_capsule_manager()
    return manager.get_system_state()


def verify_capsule_integrity() -> Dict:
    """Manually trigger capsule integrity verification."""
    manager = get_capsule_manager()
    return manager.verify_all_capsules()


if __name__ == "__main__":
    # Demo the capsule management system
    print("💾 EpochCore RAS Capsule Management Demo")
    print("=" * 50)
    
    # Initialize
    hook = initialize_capsule_management()
    manager = get_capsule_manager()
    
    print("\n📦 Initial Capsule Status:")
    status = get_capsule_status()
    print(f"  Total Capsules: {status['total_capsules']}")
    print(f"  Total Size: {status['total_size_mb']:.1f} MB")
    print(f"  Integrity Rate: {status['integrity_rate']:.1%}")
    print(f"  Corrupted Capsules: {status['corrupted_capsules']}")
    
    print("\n🔧 Running Improvement Cycle...")
    improvement_result = improve_capsule_storage()
    
    print(f"\n✅ Improvement Result: {improvement_result['status']}")
    if improvement_result['status'] == 'success':
        for improvement in improvement_result['improvements']:
            print(f"  Strategy: {improvement['strategy']}")
            if 'improvements_made' in improvement['after_state']:
                for imp in improvement['after_state']['improvements_made']:
                    print(f"    - {imp}")
    
    print("\n📦 Final Capsule Status:")
    final_status = get_capsule_status()
    print(f"  Total Capsules: {final_status['total_capsules']}")
    print(f"  Total Size: {final_status['total_size_mb']:.1f} MB")
    print(f"  Integrity Rate: {final_status['integrity_rate']:.1%}")
    print(f"  Corrupted Capsules: {final_status['corrupted_capsules']}")