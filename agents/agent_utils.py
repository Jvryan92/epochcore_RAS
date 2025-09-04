#!/usr/bin/env python3
"""
Agent Utils - Common utilities for EpochCore RAS agents
"""

import os
import sys
import json


def safe_audit_evolution(agent_name: str, cycles: int, result_data: dict):
    """Safely call the audit evolution manager with proper error handling."""
    try:
        # Add the agents directory to the path
        agents_dir = os.path.dirname(__file__)
        if agents_dir not in sys.path:
            sys.path.insert(0, agents_dir)
        
        from audit_evolution_manager import recursive_audit_evolution
        recursive_audit_evolution(agent_name, cycles, result_data)
        print(f"    ✓ Audit evolution logged for {agent_name}")
    except ImportError as e:
        print(f"    ℹ️  Audit evolution manager not available: {e}")
    except Exception as e:
        print(f"    ⚠️  Failed to log audit evolution: {e}")


def write_agent_manifest(agent_name: str, result_data: dict, manifests_dir: str = "manifests"):
    """Write agent results to manifests directory for flash sync."""
    try:
        os.makedirs(manifests_dir, exist_ok=True)
        
        # Write individual agent result
        result_file = os.path.join(manifests_dir, f"{agent_name}_results.json")
        with open(result_file, "w") as f:
            json.dump(result_data, f, indent=2)
        
        print(f"    ✓ Results written to {result_file}")
        
        # Log to audit evolution
        cycles = result_data.get("cycles_completed", 0)
        safe_audit_evolution(agent_name, cycles, result_data)
        
    except Exception as e:
        print(f"    ❌ Failed to write manifest: {e}")