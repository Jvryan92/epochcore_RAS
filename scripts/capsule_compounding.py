#!/usr/bin/env python3
"""
Capsule Compounding System

This module implements advanced compounding techniques for capsules
to amplify their effects, create recursive growth patterns, and enable
multi-dimensional mesh interactions.

Integrates with both the Ledger Agent and Meta Capsule systems to:
1. Register compound capsule strategies
2. Apply growth multipliers based on compounding technique
3. Track ethical impact of compound strategies
4. Generate provenance records for compound operations
"""

import hashlib
import json
import logging
import math
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] CapsuleCompounding: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("capsule_compounding.log")],
)
logger = logging.getLogger("capsule_compounding")

# Integration constants
DEFAULT_BASE_YIELD = 0.01007  # Base yield rate (1.007%)
DEFAULT_COMPOUND_FREQUENCY = 12  # Default compounding frequency
ROOT = Path(os.getcwd())
LEDGER_PATH = ROOT / "ledger_main.jsonl"
CAPSULES_DIR = ROOT / "out" / "capsules"
ARCHIVES_DIR = ROOT / "out" / "archive"
MESH_DIR = ROOT / "ledger" / "mesh_multistack"

# Define the compounding tricks
COMPOUNDING_TRICKS = [
    "Recursive Yield Amplification",
    "Temporal Mesh Rebalancing",
    "Quantum Liquidity Loop",
    "Autonomous Capsule Fusion",
    "MeshCredit Cascade",
    "Ledger Provenance Chaining",
    "Adaptive Interest Compounding",
    "Multi-Domain Mesh Synthesis",
    "Capsule Swarm Optimization",
    "Self-Referential Growth",
    "Dynamic Capsule Forking",
    "Resilience Mesh Overlay",
    "StrategyDeck Interlink",
    "Ethical Reflection Loop",
    "Evolutionary Capsule Mutation",
    "Temporal Ledger Stacking",
    "Collaborative Mesh Expansion",
    "Intelligence Capsule Chaining",
    "Autonomous Strategy Rotation",
    "Capsule Provenance Recursion",
    "MeshCredit Recursive Mint",
    "Capsule Ledger Interlock",
    "Self-Improvement Cascade",
    "Quantum Mesh Fork",
    "Adaptive Mesh Reallocation",
    "StrategyDeck Provenance",
    "Temporal Compounding Chain",
    "Capsule Swarm Compounding",
    "Autonomous Mesh Rebalancer",
    "Recursive Ledger Growth",
    "Capsule Evolution Overlay",
    "Ethical Compounding Loop",
    "Collaborative Capsule Fusion",
    "Intelligence Mesh Cascade",
    "StrategyDeck Capsule Chain",
    "Self-Referential Ledger",
    "Quantum Capsule Amplification",
    "Adaptive Mesh Forking",
    "Temporal Mesh Overlay",
    "Capsule Provenance Amplifier",
    "Recursive Mesh Expansion",
]

# Map compounding tricks to their growth multipliers and ethical impacts
TRICK_PROPERTIES = {
    "Recursive Yield Amplification": {
        "multiplier": 2.5,
        "ethical_impact": 0.8,
        "mesh_cost": 65,
        "category": "yield",
    },
    "Temporal Mesh Rebalancing": {
        "multiplier": 1.7,
        "ethical_impact": 0.9,
        "mesh_cost": 40,
        "category": "mesh",
    },
    "Quantum Liquidity Loop": {
        "multiplier": 3.0,
        "ethical_impact": 0.7,
        "mesh_cost": 85,
        "category": "quantum",
    },
    "Autonomous Capsule Fusion": {
        "multiplier": 2.2,
        "ethical_impact": 0.85,
        "mesh_cost": 70,
        "category": "fusion",
    },
    "MeshCredit Cascade": {
        "multiplier": 1.9,
        "ethical_impact": 0.9,
        "mesh_cost": 55,
        "category": "credit",
    },
    "Ledger Provenance Chaining": {
        "multiplier": 1.6,
        "ethical_impact": 0.95,
        "mesh_cost": 35,
        "category": "ledger",
    },
    "Adaptive Interest Compounding": {
        "multiplier": 2.1,
        "ethical_impact": 0.88,
        "mesh_cost": 60,
        "category": "yield",
    },
    "Multi-Domain Mesh Synthesis": {
        "multiplier": 1.8,
        "ethical_impact": 0.85,
        "mesh_cost": 65,
        "category": "mesh",
    },
    "Capsule Swarm Optimization": {
        "multiplier": 2.3,
        "ethical_impact": 0.8,
        "mesh_cost": 75,
        "category": "swarm",
    },
    "Self-Referential Growth": {
        "multiplier": 2.8,
        "ethical_impact": 0.75,
        "mesh_cost": 80,
        "category": "growth",
    },
    "Dynamic Capsule Forking": {
        "multiplier": 2.0,
        "ethical_impact": 0.85,
        "mesh_cost": 60,
        "category": "fork",
    },
    "Resilience Mesh Overlay": {
        "multiplier": 1.7,
        "ethical_impact": 0.9,
        "mesh_cost": 45,
        "category": "resilience",
    },
    "StrategyDeck Interlink": {
        "multiplier": 1.9,
        "ethical_impact": 0.88,
        "mesh_cost": 55,
        "category": "strategy",
    },
    "Ethical Reflection Loop": {
        "multiplier": 1.5,
        "ethical_impact": 0.98,
        "mesh_cost": 30,
        "category": "ethical",
    },
    "Evolutionary Capsule Mutation": {
        "multiplier": 2.4,
        "ethical_impact": 0.82,
        "mesh_cost": 70,
        "category": "evolution",
    },
    "Temporal Ledger Stacking": {
        "multiplier": 1.8,
        "ethical_impact": 0.88,
        "mesh_cost": 50,
        "category": "ledger",
    },
    "Collaborative Mesh Expansion": {
        "multiplier": 1.7,
        "ethical_impact": 0.92,
        "mesh_cost": 45,
        "category": "mesh",
    },
    "Intelligence Capsule Chaining": {
        "multiplier": 2.2,
        "ethical_impact": 0.86,
        "mesh_cost": 65,
        "category": "intelligence",
    },
    "Autonomous Strategy Rotation": {
        "multiplier": 1.9,
        "ethical_impact": 0.89,
        "mesh_cost": 55,
        "category": "strategy",
    },
    "Capsule Provenance Recursion": {
        "multiplier": 2.1,
        "ethical_impact": 0.87,
        "mesh_cost": 60,
        "category": "recursion",
    },
    "MeshCredit Recursive Mint": {
        "multiplier": 2.3,
        "ethical_impact": 0.84,
        "mesh_cost": 70,
        "category": "credit",
    },
    "Capsule Ledger Interlock": {
        "multiplier": 1.6,
        "ethical_impact": 0.93,
        "mesh_cost": 40,
        "category": "ledger",
    },
    "Self-Improvement Cascade": {
        "multiplier": 2.7,
        "ethical_impact": 0.8,
        "mesh_cost": 75,
        "category": "improvement",
    },
    "Quantum Mesh Fork": {
        "multiplier": 2.8,
        "ethical_impact": 0.75,
        "mesh_cost": 85,
        "category": "quantum",
    },
    "Adaptive Mesh Reallocation": {
        "multiplier": 1.8,
        "ethical_impact": 0.9,
        "mesh_cost": 50,
        "category": "mesh",
    },
    "StrategyDeck Provenance": {
        "multiplier": 1.7,
        "ethical_impact": 0.92,
        "mesh_cost": 45,
        "category": "strategy",
    },
    "Temporal Compounding Chain": {
        "multiplier": 2.0,
        "ethical_impact": 0.88,
        "mesh_cost": 60,
        "category": "temporal",
    },
    "Capsule Swarm Compounding": {
        "multiplier": 2.4,
        "ethical_impact": 0.83,
        "mesh_cost": 70,
        "category": "swarm",
    },
    "Autonomous Mesh Rebalancer": {
        "multiplier": 1.9,
        "ethical_impact": 0.89,
        "mesh_cost": 55,
        "category": "mesh",
    },
    "Recursive Ledger Growth": {
        "multiplier": 2.2,
        "ethical_impact": 0.85,
        "mesh_cost": 65,
        "category": "ledger",
    },
    "Capsule Evolution Overlay": {
        "multiplier": 2.1,
        "ethical_impact": 0.86,
        "mesh_cost": 60,
        "category": "evolution",
    },
    "Ethical Compounding Loop": {
        "multiplier": 1.6,
        "ethical_impact": 0.96,
        "mesh_cost": 35,
        "category": "ethical",
    },
    "Collaborative Capsule Fusion": {
        "multiplier": 1.8,
        "ethical_impact": 0.91,
        "mesh_cost": 50,
        "category": "fusion",
    },
    "Intelligence Mesh Cascade": {
        "multiplier": 2.3,
        "ethical_impact": 0.84,
        "mesh_cost": 65,
        "category": "intelligence",
    },
    "StrategyDeck Capsule Chain": {
        "multiplier": 1.9,
        "ethical_impact": 0.88,
        "mesh_cost": 55,
        "category": "strategy",
    },
    "Self-Referential Ledger": {
        "multiplier": 2.0,
        "ethical_impact": 0.87,
        "mesh_cost": 60,
        "category": "ledger",
    },
    "Quantum Capsule Amplification": {
        "multiplier": 2.9,
        "ethical_impact": 0.73,
        "mesh_cost": 90,
        "category": "quantum",
    },
    "Adaptive Mesh Forking": {
        "multiplier": 2.1,
        "ethical_impact": 0.86,
        "mesh_cost": 60,
        "category": "mesh",
    },
    "Temporal Mesh Overlay": {
        "multiplier": 1.8,
        "ethical_impact": 0.9,
        "mesh_cost": 50,
        "category": "temporal",
    },
    "Capsule Provenance Amplifier": {
        "multiplier": 2.0,
        "ethical_impact": 0.88,
        "mesh_cost": 55,
        "category": "provenance",
    },
    "Recursive Mesh Expansion": {
        "multiplier": 2.2,
        "ethical_impact": 0.85,
        "mesh_cost": 65,
        "category": "mesh",
    },
}


class CapsuleCompoundingEngine:
    """Engine for applying compounding strategies to capsules"""

    def __init__(
        self,
        base_yield: float = DEFAULT_BASE_YIELD,
        compound_frequency: int = DEFAULT_COMPOUND_FREQUENCY,
        ledger_path: str = str(LEDGER_PATH),
        mesh_dir: str = str(MESH_DIR),
    ):
        """Initialize the compounding engine"""
        self.base_yield = base_yield
        self.compound_frequency = compound_frequency
        self.ledger_path = Path(ledger_path)
        self.mesh_dir = Path(mesh_dir)

        # Ensure mesh directory exists
        self.mesh_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Capsule Compounding Engine initialized with base yield: "
            f"{self.base_yield * 100:.4f}%"
        )
        logger.info(f"Compounding frequency: {self.compound_frequency}")

        # Load mesh triggers if available
        self.mesh_triggers = self._load_mesh_triggers()

        # Initialize cache for optimization
        self._capsule_cache: Dict[str, Any] = {}
        self._trick_cache: Dict[str, Dict[str, Any]] = {}

    def _load_mesh_triggers(self) -> Dict[str, Any]:
        """Load mesh triggers from the mesh directory"""
        triggers_file = self.mesh_dir / "mesh_triggers.json"
        if not triggers_file.exists():
            return {"triggers": [], "base_stats": {}}

        try:
            with open(triggers_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"Could not load mesh triggers from {triggers_file}")
            return {"triggers": [], "base_stats": {}}

    def _save_mesh_triggers(self) -> None:
        """Save mesh triggers to the mesh directory"""
        triggers_file = self.mesh_dir / "mesh_triggers.json"
        try:
            with open(triggers_file, "w") as f:
                json.dump(self.mesh_triggers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving mesh triggers: {e}")

    def get_trick_properties(self, trick_name: str) -> Dict[str, Any]:
        """Get properties for a specific compounding trick"""
        if trick_name not in TRICK_PROPERTIES:
            logger.warning(f"Unknown compounding trick: {trick_name}")
            return {
                "multiplier": 1.0,
                "ethical_impact": 0.5,
                "mesh_cost": 50,
                "category": "unknown",
            }

        return TRICK_PROPERTIES[trick_name]

    def register_compound_trick(
        self, trick_name: str, capsule_id: str, mesh_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a compounding trick for a capsule"""
        if trick_name not in COMPOUNDING_TRICKS:
            logger.error(f"Invalid trick name: {trick_name}")
            return {"status": "error", "message": "Invalid trick name"}

        # Get trick properties
        trick_props = self.get_trick_properties(trick_name)

        # Generate mesh_id if not provided
        if not mesh_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            mesh_id = f"compound_{capsule_id}_{timestamp}"

        # Create trigger record
        trigger = {
            "id": mesh_id,
            "type": trick_props["category"],
            "description": f"{trick_name} applied to {capsule_id}",
            "resource_requirement": trick_props["mesh_cost"],
            "multiplier": trick_props["multiplier"],
            "ethical_impact": trick_props["ethical_impact"],
            "created_at": datetime.now().isoformat(),
            "applied_to": capsule_id,
            "trick_name": trick_name,
            "fingerprint": self._generate_fingerprint(trick_name, capsule_id),
            "activations": 0,
        }

        # Add to mesh triggers
        self.mesh_triggers["triggers"].append(trigger)

        # Update base stats
        if trick_props["category"] not in self.mesh_triggers.get("base_stats", {}):
            self.mesh_triggers.setdefault("base_stats", {})[trick_props["category"]] = {
                "count": 0,
                "total_resources": 0,
                "total_ethical_impact": 0,
            }

        self.mesh_triggers["base_stats"][trick_props["category"]]["count"] += 1
        base_stats = self.mesh_triggers["base_stats"][trick_props["category"]]
        base_stats["total_resources"] += trick_props["mesh_cost"]
        base_stats = self.mesh_triggers["base_stats"][trick_props["category"]]
        base_stats["total_ethical_impact"] += trick_props["ethical_impact"]

        # Save updated triggers
        self._save_mesh_triggers()

        logger.info(
            f"Registered compounding trick: {trick_name} for capsule {capsule_id}"
        )
        return {"status": "success", "trigger_id": mesh_id, "trigger": trigger}

    def _generate_fingerprint(self, trick_name: str, capsule_id: str) -> str:
        """Generate a unique fingerprint for this trick application"""
        data = f"{trick_name}|{capsule_id}|{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def apply_compound_trick(
        self, trick_name: str, capsule_id: str, base_value: float, duration: int = 1
    ) -> Dict[str, Any]:
        """Apply a compounding trick to a capsule and calculate the resulting value"""
        # First register the trick
        registration = self.register_compound_trick(trick_name, capsule_id)
        if registration["status"] == "error":
            return {"status": "error", "message": registration["message"]}

        trigger_id = registration["trigger_id"]
        # Get the trigger details from registration
        _ = registration["trigger"]

        # Get trick properties
        trick_props = self.get_trick_properties(trick_name)
        multiplier = trick_props["multiplier"]
        ethical_impact = trick_props["ethical_impact"]

        # Calculate compounded value
        final_value = self._calculate_compound_value(base_value, multiplier, duration)

        # Ethical adjustment
        ethical_adjustment = 1.0 - ((1.0 - ethical_impact) * 0.5)  # Less severe penalty
        adjusted_value = final_value * ethical_adjustment

        # Create result record
        result = {
            "status": "success",
            "trigger_id": trigger_id,
            "capsule_id": capsule_id,
            "trick_name": trick_name,
            "base_value": base_value,
            "multiplier": multiplier,
            "duration": duration,
            "final_value": final_value,
            "ethical_impact": ethical_impact,
            "ethical_adjustment": ethical_adjustment,
            "adjusted_value": adjusted_value,
            "applied_at": datetime.now().isoformat(),
            "category": trick_props["category"],
            "mesh_cost": trick_props["mesh_cost"],
        }

        # Create a seal for this application
        seal = self._create_compounding_seal(trigger_id, result)
        result["seal"] = seal

        # Activate the trigger
        self._activate_trigger(trigger_id)

        logger.info(
            f"Applied {trick_name} to {capsule_id}: "
            f"{base_value:.2f} → {adjusted_value:.2f}"
        )
        return result

    def _calculate_compound_value(
        self, base_value: float, multiplier: float, duration: int
    ) -> float:
        """Calculate the compounded value using the compound interest formula"""
        # Adjusted formula: P * (1 + r*m)^(t*f)
        # where P = principal, r = base yield, m = multiplier,
        # t = duration, f = frequency
        r = self.base_yield  # Base yield rate
        m = multiplier       # Trick multiplier
        t = duration         # Duration in time units
        f = self.compound_frequency  # Compounding frequency

        final_value = base_value * math.pow(1 + (r * m), t * f)
        return final_value

    def _create_compounding_seal(
        self, trigger_id: str, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a cryptographic seal for this compounding application"""
        # Create a seal with relevant information
        seal_data = {
            "trigger_id": trigger_id,
            "capsule_id": result["capsule_id"],
            "trick_name": result["trick_name"],
            "timestamp": result["applied_at"],
            "base_value": result["base_value"],
            "final_value": result["adjusted_value"],
            "ethical_impact": result["ethical_impact"],
        }

        # Hash the seal data
        seal_data_str = json.dumps(seal_data, sort_keys=True)
        seal_hash = hashlib.sha256(seal_data_str.encode()).hexdigest()

        # Create the seal record
        seal = {
            "hash": seal_hash,
            "created_at": datetime.now().isoformat(),
            "data": seal_data,
        }

        # Save the seal to mesh directory
        seal_file = (
            self.mesh_dir / "seals" / f"compound_{trigger_id}_{int(time.time())}.json"
        )
        seal_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(seal_file, "w") as f:
                json.dump(seal, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving compounding seal: {e}")

        return seal

    def _activate_trigger(self, trigger_id: str) -> bool:
        """Activate a trigger in the mesh system"""
        # Find the trigger
        trigger = None
        for t in self.mesh_triggers["triggers"]:
            if t["id"] == trigger_id:
                trigger = t
                break

        if not trigger:
            logger.error(f"Trigger not found: {trigger_id}")
            return False

        # Increment activations
        trigger["activations"] += 1

        # Create activation record
        activation = {
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "activation_number": trigger["activations"],
            "status": "completed",
        }

        # Save activation record
        activation_file = (
            self.mesh_dir / "activations" / f"{trigger_id}_{int(time.time())}.json"
        )
        activation_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(activation_file, "w") as f:
                json.dump(activation, f, indent=2)

            # Update mesh triggers
            self._save_mesh_triggers()
            return True
        except Exception as e:
            logger.error(f"Error saving activation record: {e}")
            return False

    def get_compounding_tricks_by_category(self, category: str) -> List[str]:
        """Get a list of compounding tricks by category"""
        return [
            name
            for name, props in TRICK_PROPERTIES.items()
            if props["category"] == category
        ]

    def get_optimal_compounding_strategy(
        self,
        base_value: float,
        target_value: float,
        max_duration: int = 12,
        ethical_threshold: float = 0.8,
    ) -> Dict[str, Any]:
        """Find the optimal compounding strategy to reach a target value"""
        valid_tricks = [
            name
            for name, props in TRICK_PROPERTIES.items()
            if props["ethical_impact"] >= ethical_threshold
        ]

        if not valid_tricks:
            return {"status": "error", "message": "No tricks meet ethical threshold"}

        best_strategy = None
        best_duration = max_duration
        best_final_value = 0

        for trick_name in valid_tricks:
            props = self.get_trick_properties(trick_name)
            multiplier = props["multiplier"]

            # Try different durations
            for duration in range(1, max_duration + 1):
                final_value = self._calculate_compound_value(
                    base_value, multiplier, duration
                )

                # Apply ethical adjustment
                adjusted_value = final_value * (
                    1.0 - ((1.0 - props["ethical_impact"]) * 0.5)
                )

                # Check if this is better than current best
                if adjusted_value >= target_value and (
                    best_strategy is None
                    or duration < best_duration
                    or (duration == best_duration and adjusted_value > best_final_value)
                ):
                    best_strategy = trick_name
                    best_duration = duration
                    best_final_value = adjusted_value

        if best_strategy is None:
            return {
                "status": "not_possible",
                "message": (
                    f"Cannot reach target value {target_value} "
                    f"from {base_value} within constraints"
                ),
            }

        return {
            "status": "success",
            "trick_name": best_strategy,
            "duration": best_duration,
            "final_value": best_final_value,
            "ethical_impact": TRICK_PROPERTIES[best_strategy]["ethical_impact"],
            "multiplier": TRICK_PROPERTIES[best_strategy]["multiplier"],
            "base_value": base_value,
            "target_value": target_value,
            "mesh_cost": TRICK_PROPERTIES[best_strategy]["mesh_cost"],
        }

    def chain_compound_tricks(
        self,
        capsule_id: str,
        trick_sequence: List[str],
        base_value: float,
        duration_per_trick: int = 1,
    ) -> Dict[str, Any]:
        """Apply a sequence of compounding tricks to a capsule"""
        if not trick_sequence:
            return {"status": "error", "message": "Empty trick sequence"}

        current_value = base_value
        results = []

        for trick_name in trick_sequence:
            # Apply the trick
            result = self.apply_compound_trick(
                trick_name, capsule_id, current_value, duration_per_trick
            )

            if result["status"] == "error":
                # Stop the chain if there's an error
                break

            results.append(result)
            current_value = result["adjusted_value"]

        # Calculate overall growth and ethical impact
        overall_growth = (current_value / base_value) - 1.0
        avg_ethical_impact = (
            sum(r["ethical_impact"] for r in results) / len(results) if results else 0
        )

        return {
            "status": "success" if results else "error",
            "capsule_id": capsule_id,
            "trick_sequence": trick_sequence,
            "base_value": base_value,
            "final_value": current_value,
            "overall_growth": overall_growth,
            "avg_ethical_impact": avg_ethical_impact,
            "steps_completed": len(results),
            "steps_total": len(trick_sequence),
            "individual_results": results,
        }

    def generate_compounding_report(
        self, capsule_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a report on compounding activities"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_tricks_registered": len(self.mesh_triggers["triggers"]),
            "total_activations": sum(
                t["activations"] for t in self.mesh_triggers["triggers"]
            ),
            "categories": {},
            "top_tricks": [],
            "ethical_impact": {"average": 0, "min": 1.0, "max": 0},
        }

        # Filter by capsule if specified
        triggers = self.mesh_triggers["triggers"]
        if capsule_id:
            triggers = [t for t in triggers if t.get("applied_to") == capsule_id]
            report["capsule_id"] = capsule_id
            report["total_tricks_for_capsule"] = len(triggers)

        # Aggregate by category
        category_stats = {}
        ethical_impacts = []

        for trigger in triggers:
            category = trigger.get("type", "unknown")
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "activations": 0,
                    "avg_multiplier": 0,
                    "total_resources": 0,
                }

            category_stats[category]["count"] += 1
            category_stats[category]["activations"] += trigger.get("activations", 0)
            category_stats[category]["avg_multiplier"] += trigger.get("multiplier", 1.0)
            category_stats[category]["total_resources"] += trigger.get(
                "resource_requirement", 0
            )

            ethical_impacts.append(trigger.get("ethical_impact", 0.5))

        # Finalize category stats
        for category, stats in category_stats.items():
            if stats["count"] > 0:
                stats["avg_multiplier"] /= stats["count"]
            report["categories"][category] = stats

        # Calculate ethical impact stats
        if ethical_impacts:
            report["ethical_impact"]["average"] = sum(ethical_impacts) / len(
                ethical_impacts
            )
            report["ethical_impact"]["min"] = min(ethical_impacts)
            report["ethical_impact"]["max"] = max(ethical_impacts)

        # Find top tricks by activation
        top_tricks = sorted(
            triggers, key=lambda t: t.get("activations", 0), reverse=True
        )[:5]

        report["top_tricks"] = [
            {
                "id": t["id"],
                "trick_name": t.get("trick_name", "Unknown"),
                "activations": t.get("activations", 0),
                "multiplier": t.get("multiplier", 1.0),
                "ethical_impact": t.get("ethical_impact", 0.5),
            }
            for t in top_tricks
        ]

        return report


def main() -> None:
    """CLI interface for capsule compounding"""
    import argparse

    parser = argparse.ArgumentParser(description="Capsule Compounding System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List tricks command
    list_parser = subparsers.add_parser("list", help="List all compounding tricks")
    list_parser.add_argument("--category", help="Filter by category")

    # Apply trick command
    apply_parser = subparsers.add_parser("apply", help="Apply a compounding trick")
    apply_parser.add_argument("trick_name", help="Name of the trick to apply")
    apply_parser.add_argument("capsule_id", help="ID of the capsule")
    apply_parser.add_argument(
        "--base-value", type=float, default=10.0, help="Base value"
    )
    apply_parser.add_argument("--duration", type=int, default=1, help="Duration")

    # Chain tricks command
    chain_parser = subparsers.add_parser("chain", help="Apply a chain of tricks")
    chain_parser.add_argument("capsule_id", help="ID of the capsule")
    chain_parser.add_argument(
        "--tricks", nargs="+", required=True, help="List of tricks to apply"
    )
    chain_parser.add_argument(
        "--base-value", type=float, default=10.0, help="Base value"
    )

    # Optimize command
    optimize_parser = subparsers.add_parser(
        "optimize", help="Find optimal compounding strategy"
    )
    optimize_parser.add_argument(
        "--base-value", type=float, required=True, help="Base value"
    )
    optimize_parser.add_argument(
        "--target-value", type=float, required=True, help="Target value"
    )
    optimize_parser.add_argument(
        "--max-duration", type=int, default=12, help="Maximum duration"
    )
    optimize_parser.add_argument(
        "--ethical-threshold", type=float, default=0.8, help="Ethical threshold"
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate compounding report")
    report_parser.add_argument("--capsule-id", help="Filter by capsule ID")

    args = parser.parse_args()

    # Initialize the compounding engine
    engine = CapsuleCompoundingEngine()

    if args.command == "list":
        if args.category:
            tricks = engine.get_compounding_tricks_by_category(args.category)
            print(f"Compounding Tricks in category '{args.category}':")
        else:
            tricks = COMPOUNDING_TRICKS
            print("All Compounding Tricks:")

        for trick in tricks:
            props = engine.get_trick_properties(trick)
            print(f"  {trick}")
            print(f"    Multiplier: {props['multiplier']:.2f}x")
            print(f"    Ethical Impact: {props['ethical_impact']:.2f}")
            print(f"    Mesh Cost: {props['mesh_cost']}")
            print(f"    Category: {props['category']}")

    elif args.command == "apply":
        result = engine.apply_compound_trick(
            args.trick_name, args.capsule_id, args.base_value, args.duration
        )

        if result["status"] == "success":
            print(f"Applied {args.trick_name} to {args.capsule_id}:")
            print(f"  Base Value: {result['base_value']:.2f}")
            print(f"  Multiplier: {result['multiplier']:.2f}x")
            print(f"  Duration: {result['duration']}")
            print(
                print(
                    "  Final Value (before ethical adjustment): "
                    f"{result['final_value']:.2f}"
                )
            )
            print(f"  Ethical Impact: {result['ethical_impact']:.2f}")
            print(f"  Final Adjusted Value: {result['adjusted_value']:.2f}")
            print(
                print(
                    "  Growth: "
                    f"{(result['adjusted_value']/result['base_value'] - 1) * 100:.2f}%"
                )
            )
        else:
            print(f"Error: {result['message']}")

    elif args.command == "chain":
        result = engine.chain_compound_tricks(
            args.capsule_id, args.tricks, args.base_value
        )

        if result["status"] == "success":
            print(f"Applied trick chain to {args.capsule_id}:")
            print(f"  Tricks: {', '.join(args.tricks)}")
            print(f"  Base Value: {result['base_value']:.2f}")
            print(f"  Final Value: {result['final_value']:.2f}")
            print(f"  Overall Growth: {result['overall_growth'] * 100:.2f}%")
            print(f"  Average Ethical Impact: {result['avg_ethical_impact']:.2f}")
            print(
                print(
                    "  Steps Completed: "
                    f"{result['steps_completed']}/{result['steps_total']}"
                )
            )
        else:
            print(f"Error: {result['message']}")

    elif args.command == "optimize":
        result = engine.get_optimal_compounding_strategy(
            args.base_value,
            args.target_value,
            args.max_duration,
            args.ethical_threshold,
        )

        if result["status"] == "success":
            print("Optimal Compounding Strategy:")
            print(f"  Trick: {result['trick_name']}")
            print(f"  Duration: {result['duration']}")
            print(f"  Base Value: {result['base_value']:.2f}")
            print(f"  Target Value: {result['target_value']:.2f}")
            print(f"  Final Value: {result['final_value']:.2f}")
            print(f"  Ethical Impact: {result['ethical_impact']:.2f}")
            print(f"  Multiplier: {result['multiplier']:.2f}x")
            print(f"  Mesh Cost: {result['mesh_cost']}")
        else:
            print(f"Result: {result['status']}")
            print(f"Message: {result['message']}")

    elif args.command == "report":
        report = engine.generate_compounding_report(args.capsule_id)

        print(f"Compounding Report (generated at {report['generated_at']}):")
        if args.capsule_id:
            print(f"  Capsule ID: {report['capsule_id']}")
            print(f"  Total Tricks for Capsule: {report['total_tricks_for_capsule']}")
        else:
            print(f"  Total Tricks Registered: {report['total_tricks_registered']}")

        print(f"  Total Activations: {report['total_activations']}")

        print("\nCategories:")
        for category, stats in report["categories"].items():
            print(f"  {category}:")
            print(f"    Count: {stats['count']}")
            print(f"    Activations: {stats['activations']}")
            print(f"    Average Multiplier: {stats['avg_multiplier']:.2f}x")
            print(f"    Total Resources: {stats['total_resources']}")

        print("\nTop Tricks:")
        for i, trick in enumerate(report["top_tricks"], 1):
            print(f"  {i}. {trick['trick_name']} (ID: {trick['id']})")
            print(f"     Activations: {trick['activations']}")
            print(f"     Multiplier: {trick['multiplier']:.2f}x")
            print(f"     Ethical Impact: {trick['ethical_impact']:.2f}")

        print("\nEthical Impact:")
        print(f"  Average: {report['ethical_impact']['average']:.2f}")
        print(f"  Min: {report['ethical_impact']['min']:.2f}")
        print(f"  Max: {report['ethical_impact']['max']:.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
