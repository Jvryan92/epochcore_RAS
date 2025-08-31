#!/usr/bin/env python3
"""
Meta-Capsule Creation System
Generates a meta-capsule that captures the state of all cycles
Updates the ledger with the meta-capsule, ensuring traceability
Integrates with all EPOCH5 systems for comprehensive state capture
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import zipfile
import glob

# Import related systems for state capture
try:
    from agent_management import AgentManager
    from policy_grants import PolicyManager
    from dag_management import DAGManager
    from cycle_execution import CycleExecutor
    from capsule_metadata import CapsuleManager
except ImportError:
    # Fallback for standalone operation
    AgentManager = None
    PolicyManager = None
    DAGManager = None
    CycleExecutor = None
    CapsuleManager = None


class MetaCapsuleCreator:
    def __init__(self, base_dir: str = "./archive/EPOCH5"):
        self.base_dir = Path(base_dir)
        self.meta_dir = self.base_dir / "meta_capsules"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        self.ledger_file = self.base_dir / "ledger.log"
        self.meta_ledger = self.meta_dir / "meta_ledger.log"
        self.state_snapshots = self.meta_dir / "state_snapshots"
        self.state_snapshots.mkdir(parents=True, exist_ok=True)
        
        # Create ethical snapshots directory
        self.ethical_snapshots = self.meta_dir / "ethical_snapshots"
        self.ethical_snapshots.mkdir(parents=True, exist_ok=True)

        # Initialize system managers if available
        self.agent_manager = AgentManager(base_dir) if AgentManager else None
        self.policy_manager = PolicyManager(base_dir) if PolicyManager else None
        self.dag_manager = DAGManager(base_dir) if DAGManager else None
        self.cycle_executor = CycleExecutor(base_dir) if CycleExecutor else None
        self.capsule_manager = CapsuleManager(base_dir) if CapsuleManager else None

    def timestamp(self) -> str:
        """Generate ISO timestamp consistent with EPOCH5"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash consistent with EPOCH5"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _compute_ethical_summary(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute summary of ethical metrics across all agents"""
        if not agents:
            return {
                "status": "No active agents",
                "timestamp": self.timestamp()
            }

        # Initialize counters
        total_assessments = 0
        successful_assessments = 0
        ethical_scores = []
        constraint_satisfaction = []
        reflection_confidence = []
        principle_scores = {}
        stakeholder_impacts = {}

        # Aggregate metrics
        for agent in agents:
            metrics = agent.get("ethical_metrics", {})
            
            # Count assessments
            total_assessments += metrics.get("total_ethical_assessments", 0)
            successful_assessments += metrics.get("successful_ethical_assessments", 0)
            
            # Collect scores
            ethical_scores.append(metrics.get("ethical_score", 1.0))
            constraint_satisfaction.append(metrics.get("constraint_satisfaction_rate", 1.0))
            reflection_confidence.append(metrics.get("reflection_confidence", 0.5))
            
            # Aggregate principle performance
            for principle, score in metrics.get("principle_performance", {}).items():
                if principle not in principle_scores:
                    principle_scores[principle] = []
                principle_scores[principle].append(score)
                
            # Aggregate stakeholder impacts
            for stakeholder, impact in metrics.get("stakeholder_impact", {}).items():
                if stakeholder not in stakeholder_impacts:
                    stakeholder_impacts[stakeholder] = []
                stakeholder_impacts[stakeholder].append(
                    impact.get("average_impact", 0.0)
                )

        # Compute averages and summaries
        summary = {
            "timestamp": self.timestamp(),
            "total_assessments": total_assessments,
            "successful_assessments": successful_assessments,
            "success_rate": (successful_assessments / total_assessments 
                           if total_assessments > 0 else 1.0),
            "average_metrics": {
                "ethical_score": sum(ethical_scores) / len(agents),
                "constraint_satisfaction": sum(constraint_satisfaction) / len(agents),
                "reflection_confidence": sum(reflection_confidence) / len(agents)
            },
            "principle_performance": {
                principle: sum(scores) / len(scores)
                for principle, scores in principle_scores.items()
            },
            "stakeholder_impacts": {
                stakeholder: sum(impacts) / len(impacts)
                for stakeholder, impacts in stakeholder_impacts.items()
            }
        }

        # Save ethical snapshot
        snapshot_file = self.ethical_snapshots / f"ethical_summary_{self.timestamp()}.json"
        with open(snapshot_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    def capture_system_state(self) -> Dict[str, Any]:
        """Capture the current state of all EPOCH5 systems"""
        state = {
            "captured_at": self.timestamp(),
            "systems": {},
            "file_hashes": {},
            "summary_stats": {},
        }

        # Capture agent management state
        if self.agent_manager:
            agent_registry = self.agent_manager.load_registry()
            # Capture agent and ethical state
            active_agents = self.agent_manager.get_active_agents()
            ethical_summary = self._compute_ethical_summary(active_agents)
            
            state["systems"]["agents"] = {
                "registry": agent_registry,
                "active_agents": len(active_agents),
                "total_agents": len(agent_registry.get("agents", {})),
                "ethical_metrics": ethical_summary
            }

            # Hash agent files
            if (self.base_dir / "agents").exists():
                for file_path in (self.base_dir / "agents").glob("*.json"):
                    with open(file_path, "r") as f:
                        content = f.read()
                        state["file_hashes"][f"agents/{file_path.name}"] = self.sha256(
                            content
                        )

        # Capture policy and grants state
        if self.policy_manager:
            policies = self.policy_manager.load_policies()
            grants = self.policy_manager.load_grants()
            state["systems"]["policies"] = {
                "policies": policies,
                "grants": grants,
                "active_policies": len(self.policy_manager.get_active_policies()),
                "total_grants": len(grants.get("grants", {})),
            }

            # Hash policy files
            if (self.base_dir / "policies").exists():
                for file_path in (self.base_dir / "policies").glob("*.json"):
                    with open(file_path, "r") as f:
                        content = f.read()
                        state["file_hashes"][f"policies/{file_path.name}"] = (
                            self.sha256(content)
                        )

        # Capture DAG management state
        if self.dag_manager:
            dags = self.dag_manager.load_dags()
            state["systems"]["dags"] = {
                "dags": dags,
                "total_dags": len(dags.get("dags", {})),
                "completed_dags": len(
                    [
                        d
                        for d in dags.get("dags", {}).values()
                        if d.get("status") == "completed"
                    ]
                ),
            }

            # Hash DAG files
            if (self.base_dir / "dags").exists():
                for file_path in (self.base_dir / "dags").glob("*.json"):
                    with open(file_path, "r") as f:
                        content = f.read()
                        state["file_hashes"][f"dags/{file_path.name}"] = self.sha256(
                            content
                        )

        # Capture cycle execution state
        if self.cycle_executor:
            cycles = self.cycle_executor.load_cycles()
            state["systems"]["cycles"] = {
                "cycles": cycles,
                "total_cycles": len(cycles.get("cycles", {})),
                "completed_cycles": len(
                    [
                        c
                        for c in cycles.get("cycles", {}).values()
                        if c.get("status") == "completed"
                    ]
                ),
            }

            # Hash cycle files
            if (self.base_dir / "cycles").exists():
                for file_path in (self.base_dir / "cycles").glob("*.json"):
                    with open(file_path, "r") as f:
                        content = f.read()
                        state["file_hashes"][f"cycles/{file_path.name}"] = self.sha256(
                            content
                        )

        # Capture capsule and metadata state
        if self.capsule_manager:
            capsules = self.capsule_manager.list_capsules()
            archives = self.capsule_manager.list_archives()
            state["systems"]["capsules"] = {
                "total_capsules": len(capsules),
                "total_archives": len(archives),
                "capsule_summary": capsules[:10],  # Sample of capsules
                "archive_summary": archives[:10],  # Sample of archives
            }

            # Hash capsule files
            for dir_name in ["capsules", "metadata", "archives"]:
                dir_path = self.base_dir / dir_name
                if dir_path.exists():
                    for file_path in dir_path.glob("*.json"):
                        with open(file_path, "r") as f:
                            content = f.read()
                            state["file_hashes"][f"{dir_name}/{file_path.name}"] = (
                                self.sha256(content)
                            )

        # Capture base EPOCH5 system state
        state["systems"]["epoch5_base"] = self.capture_epoch5_base_state()

        # Generate summary statistics
        state["summary_stats"] = {
            "total_files_captured": len(state["file_hashes"]),
            "systems_captured": len(state["systems"]),
            "capture_timestamp": state["captured_at"],
            "state_hash": self.sha256(json.dumps(state["systems"], sort_keys=True)),
        }

        return state

    def capture_epoch5_base_state(self) -> Dict[str, Any]:
        """Capture state from the original EPOCH5 system"""
        base_state = {
            "ledger": {"exists": False, "entries": 0, "hash": None},
            "heartbeat": {"exists": False, "entries": 0, "hash": None},
            "manifests": {"count": 0, "files": []},
            "unity_seal": {"exists": False, "hash": None},
        }

        # Check ledger
        if self.ledger_file.exists():
            with open(self.ledger_file, "r") as f:
                content = f.read()
                lines = content.strip().split("\n") if content.strip() else []
                base_state["ledger"] = {
                    "exists": True,
                    "entries": len(lines),
                    "hash": self.sha256(content),
                    "last_entry": lines[-1] if lines else None,
                }

        # Check heartbeat
        heartbeat_file = self.base_dir / "heartbeat.log"
        if heartbeat_file.exists():
            with open(heartbeat_file, "r") as f:
                content = f.read()
                lines = content.strip().split("\n") if content.strip() else []
                base_state["heartbeat"] = {
                    "exists": True,
                    "entries": len(lines),
                    "hash": self.sha256(content),
                }

        # Check manifests
        manifests_dir = self.base_dir / "manifests"
        if manifests_dir.exists():
            manifest_files = list(manifests_dir.glob("*.txt"))
            base_state["manifests"] = {
                "count": len(manifest_files),
                "files": [f.name for f in manifest_files],
            }

        # Check unity seal
        unity_seal_file = self.base_dir / "unity_seal.txt"
        if unity_seal_file.exists():
            with open(unity_seal_file, "r") as f:
                content = f.read()
                base_state["unity_seal"] = {
                    "exists": True,
                    "hash": self.sha256(content),
                }

        return base_state

    def create_meta_capsule(
        self, meta_capsule_id: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a meta-capsule capturing the complete system state"""
        # Capture current system state
        system_state = self.capture_system_state()

        # Create meta-capsule
        meta_capsule = {
            "meta_capsule_id": meta_capsule_id,
            "created_at": self.timestamp(),
            "description": description,
            "version": "1.0",
            "type": "EPOCH5_META_CAPSULE",
            "system_state": system_state,
            "provenance_chain": self.build_provenance_chain(),
            "integrity_verification": {},
            "archive_info": None,
            "ledger_update": None,
        }

        # Calculate meta-capsule hash
        meta_data = json.dumps(
            {
                "meta_capsule_id": meta_capsule_id,
                "created_at": meta_capsule["created_at"],
                "state_hash": system_state["summary_stats"]["state_hash"],
                "file_count": system_state["summary_stats"]["total_files_captured"],
            },
            sort_keys=True,
        )

        meta_capsule["meta_hash"] = self.sha256(meta_data)

        # Create integrity verification
        meta_capsule["integrity_verification"] = self.create_integrity_verification(
            meta_capsule
        )

        # Save meta-capsule
        meta_capsule_file = self.meta_dir / f"{meta_capsule_id}.json"
        with open(meta_capsule_file, "w") as f:
            json.dump(meta_capsule, f, indent=2)

        # Create state snapshot
        snapshot_file = self.state_snapshots / f"{meta_capsule_id}_snapshot.json"
        with open(snapshot_file, "w") as f:
            json.dump(system_state, f, indent=2)

        # Create archive of all system files
        archive_info = self.create_system_archive(meta_capsule_id)
        meta_capsule["archive_info"] = archive_info

        # Update meta-capsule with archive info
        with open(meta_capsule_file, "w") as f:
            json.dump(meta_capsule, f, indent=2)

        # Update ledgers
        self.update_ledger_with_meta_capsule(meta_capsule)

        # Log creation
        self.log_meta_event(
            meta_capsule_id,
            "META_CAPSULE_CREATED",
            {
                "systems_captured": len(system_state["systems"]),
                "files_captured": len(system_state["file_hashes"]),
                "meta_hash": meta_capsule["meta_hash"],
            },
        )

        return meta_capsule

    def build_provenance_chain(self) -> List[Dict[str, Any]]:
        """Build provenance chain from ledger entries"""
        provenance = []

        if self.ledger_file.exists():
            with open(self.ledger_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and "RECORD_HASH=" in line:
                        # Parse EPOCH5 ledger entry
                        parts = line.split("|")
                        entry = {"line_number": line_num, "raw_entry": line}

                        for part in parts:
                            if "=" in part:
                                key, value = part.split("=", 1)
                                entry[key.lower()] = value

                        provenance.append(entry)

        return provenance

    def create_integrity_verification(
        self, meta_capsule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive integrity verification for the meta-capsule"""
        verification = {
            "created_at": self.timestamp(),
            "verification_method": "SHA256_CHAIN_MERKLE",
            "system_hashes": meta_capsule["system_state"]["file_hashes"],
            "provenance_hash": None,
            "combined_hash": None,
        }

        # Hash provenance chain
        provenance_data = json.dumps(meta_capsule["provenance_chain"], sort_keys=True)
        verification["provenance_hash"] = self.sha256(provenance_data)

        # Create combined hash from all system hashes
        all_hashes = list(verification["system_hashes"].values())
        all_hashes.append(verification["provenance_hash"])
        all_hashes.append(meta_capsule["system_state"]["summary_stats"]["state_hash"])

        combined_data = "|".join(sorted(all_hashes))
        verification["combined_hash"] = self.sha256(combined_data)

        return verification

    def create_system_archive(self, meta_capsule_id: str) -> Dict[str, Any]:
        """Create a comprehensive archive of the entire system state"""
        archive_file = self.meta_dir / f"{meta_capsule_id}_system_archive.zip"

        archive_info = {
            "archive_id": f"{meta_capsule_id}_system_archive",
            "created_at": self.timestamp(),
            "archive_file": str(archive_file),
            "included_directories": [],
            "file_count": 0,
            "total_size": 0,
            "archive_hash": None,
        }

        try:
            with zipfile.ZipFile(archive_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Archive all system directories
                system_dirs = [
                    "agents",
                    "policies",
                    "dags",
                    "cycles",
                    "capsules",
                    "metadata",
                    "archives",
                    "manifests",
                ]

                for dir_name in system_dirs:
                    dir_path = self.base_dir / dir_name
                    if dir_path.exists():
                        archive_info["included_directories"].append(dir_name)

                        for file_path in dir_path.rglob("*"):
                            if file_path.is_file():
                                arcname = (
                                    f"{dir_name}/{file_path.relative_to(dir_path)}"
                                )
                                zipf.write(file_path, arcname)
                                archive_info["file_count"] += 1

                # Archive base EPOCH5 files
                base_files = [
                    "ledger.log",
                    "heartbeat.log",
                    "incoming_tide.log",
                    "unity_seal.txt",
                ]
                for file_name in base_files:
                    file_path = self.base_dir / file_name
                    if file_path.exists():
                        zipf.write(file_path, file_name)
                        archive_info["file_count"] += 1

            # Calculate archive properties
            archive_info["total_size"] = archive_file.stat().st_size

            # Calculate archive hash
            with open(archive_file, "rb") as f:
                archive_content = f.read()
                archive_info["archive_hash"] = hashlib.sha256(
                    archive_content
                ).hexdigest()

            archive_info["status"] = "completed"

        except Exception as e:
            archive_info["status"] = "failed"
            archive_info["error"] = str(e)

        return archive_info

    def update_ledger_with_meta_capsule(self, meta_capsule: Dict[str, Any]):
        """Update the main ledger with meta-capsule information"""
        # Get previous hash from ledger
        prev_hash = self.get_previous_hash()

        # Create ledger entry for meta-capsule
        ledger_entry_data = f"META_CAPSULE|{meta_capsule['meta_capsule_id']}|{meta_capsule['created_at']}|{meta_capsule['meta_hash']}|PREV_HASH={prev_hash}"
        ledger_entry_hash = self.sha256(ledger_entry_data)

        # Update main ledger
        with open(self.ledger_file, "a") as f:
            f.write(
                f"TIMESTAMP={meta_capsule['created_at']}|TYPE=META_CAPSULE|META_ID={meta_capsule['meta_capsule_id']}|META_HASH={meta_capsule['meta_hash']}|PREV_HASH={prev_hash}|RECORD_HASH={ledger_entry_hash}\n"
            )

        # Update meta ledger
        with open(self.meta_ledger, "a") as f:
            f.write(
                f"TIMESTAMP={meta_capsule['created_at']}|META_CAPSULE_ID={meta_capsule['meta_capsule_id']}|META_HASH={meta_capsule['meta_hash']}|SYSTEMS_COUNT={len(meta_capsule['system_state']['systems'])}|RECORD_HASH={ledger_entry_hash}\n"
            )

        # Update meta-capsule with ledger info
        meta_capsule["ledger_update"] = {
            "main_ledger_updated": True,
            "meta_ledger_updated": True,
            "ledger_entry_hash": ledger_entry_hash,
            "prev_hash": prev_hash,
            "updated_at": self.timestamp(),
        }

    def get_previous_hash(self) -> str:
        """Get the previous hash from the ledger for chaining"""
        if not self.ledger_file.exists():
            return "0" * 64  # Genesis hash

        try:
            with open(self.ledger_file, "r") as f:
                lines = f.readlines()

            # Find the last line with RECORD_HASH
            for line in reversed(lines):
                line = line.strip()
                if "RECORD_HASH=" in line:
                    parts = line.split("|")
                    for part in parts:
                        if part.startswith("RECORD_HASH="):
                            return part.split("=", 1)[1]

            return "0" * 64  # No previous hash found

        except Exception:
            return "0" * 64  # Error reading ledger

    def verify_meta_capsule(self, meta_capsule_id: str) -> Dict[str, Any]:
        """Verify the integrity of a meta-capsule"""
        meta_capsule_file = self.meta_dir / f"{meta_capsule_id}.json"

        if not meta_capsule_file.exists():
            return {"error": "Meta-capsule not found"}

        with open(meta_capsule_file, "r") as f:
            meta_capsule = json.load(f)

        verification_result = {
            "meta_capsule_id": meta_capsule_id,
            "verified_at": self.timestamp(),
            "integrity_valid": False,
            "archive_valid": False,
            "ledger_consistent": False,
            "details": {},
        }

        # Verify meta-capsule hash
        meta_data = json.dumps(
            {
                "meta_capsule_id": meta_capsule["meta_capsule_id"],
                "created_at": meta_capsule["created_at"],
                "state_hash": meta_capsule["system_state"]["summary_stats"][
                    "state_hash"
                ],
                "file_count": meta_capsule["system_state"]["summary_stats"][
                    "total_files_captured"
                ],
            },
            sort_keys=True,
        )

        calculated_hash = self.sha256(meta_data)
        verification_result["integrity_valid"] = (
            calculated_hash == meta_capsule["meta_hash"]
        )
        verification_result["details"]["calculated_hash"] = calculated_hash
        verification_result["details"]["stored_hash"] = meta_capsule["meta_hash"]

        # Verify archive if it exists
        if (
            meta_capsule.get("archive_info")
            and meta_capsule["archive_info"]["status"] == "completed"
        ):
            archive_file = Path(meta_capsule["archive_info"]["archive_file"])
            if archive_file.exists():
                with open(archive_file, "rb") as f:
                    archive_content = f.read()
                    calculated_archive_hash = hashlib.sha256(
                        archive_content
                    ).hexdigest()
                    verification_result["archive_valid"] = (
                        calculated_archive_hash
                        == meta_capsule["archive_info"]["archive_hash"]
                    )
                    verification_result["details"]["archive_hash_valid"] = (
                        verification_result["archive_valid"]
                    )

        # Verify ledger consistency
        if meta_capsule.get("ledger_update"):
            verification_result["ledger_consistent"] = self.verify_ledger_entry(
                meta_capsule
            )

        return verification_result

    def verify_ledger_entry(self, meta_capsule: Dict[str, Any]) -> bool:
        """Verify that the meta-capsule entry exists in the ledger"""
        if not self.ledger_file.exists():
            return False

        meta_id = meta_capsule["meta_capsule_id"]
        meta_hash = meta_capsule["meta_hash"]

        with open(self.ledger_file, "r") as f:
            for line in f:
                if f"META_ID={meta_id}" in line and f"META_HASH={meta_hash}" in line:
                    return True

        return False

    def log_meta_event(self, meta_capsule_id: str, event: str, data: Dict[str, Any]):
        """Log meta-capsule events"""
        log_entry = {
            "timestamp": self.timestamp(),
            "meta_capsule_id": meta_capsule_id,
            "event": event,
            "data": data,
            "hash": self.sha256(f"{self.timestamp()}|{meta_capsule_id}|{event}"),
        }

        meta_events_log = self.meta_dir / "meta_events.log"
        with open(meta_events_log, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")

    def list_meta_capsules(self) -> List[Dict[str, Any]]:
        """List all meta-capsules"""
        meta_capsules = []

        for meta_file in self.meta_dir.glob("*.json"):
            if not meta_file.name.endswith("_snapshot.json"):
                try:
                    with open(meta_file, "r") as f:
                        meta_capsule = json.load(f)
                        meta_capsules.append(
                            {
                                "meta_capsule_id": meta_capsule["meta_capsule_id"],
                                "created_at": meta_capsule["created_at"],
                                "systems_captured": len(
                                    meta_capsule["system_state"]["systems"]
                                ),
                                "files_captured": meta_capsule["system_state"][
                                    "summary_stats"
                                ]["total_files_captured"],
                                "meta_hash": meta_capsule["meta_hash"],
                            }
                        )
                except Exception:
                    continue  # Skip invalid files

        return sorted(meta_capsules, key=lambda x: x["created_at"], reverse=True)


# CLI interface for meta-capsule management
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 Meta-Capsule Creation System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create meta-capsule
    create_parser = subparsers.add_parser("create", help="Create a new meta-capsule")
    create_parser.add_argument("meta_capsule_id", help="Meta-capsule identifier")
    create_parser.add_argument(
        "--description", default="", help="Description of the meta-capsule"
    )

    # Verify meta-capsule
    verify_parser = subparsers.add_parser("verify", help="Verify a meta-capsule")
    verify_parser.add_argument("meta_capsule_id", help="Meta-capsule identifier")

    # List meta-capsules
    subparsers.add_parser("list", help="List all meta-capsules")

    # Show state
    state_parser = subparsers.add_parser("state", help="Show current system state")

    args = parser.parse_args()
    creator = MetaCapsuleCreator()

    if args.command == "create":
        meta_capsule = creator.create_meta_capsule(
            args.meta_capsule_id, args.description
        )
        print(f"Created meta-capsule: {meta_capsule['meta_capsule_id']}")
        print(f"Systems captured: {len(meta_capsule['system_state']['systems'])}")
        print(
            f"Files captured: {meta_capsule['system_state']['summary_stats']['total_files_captured']}"
        )
        print(f"Meta-hash: {meta_capsule['meta_hash']}")

        if (
            meta_capsule.get("archive_info")
            and meta_capsule["archive_info"]["status"] == "completed"
        ):
            print(
                f"System archive: {meta_capsule['archive_info']['file_count']} files, {meta_capsule['archive_info']['total_size']} bytes"
            )

    elif args.command == "verify":
        result = creator.verify_meta_capsule(args.meta_capsule_id)
        print(f"Meta-capsule verification for {args.meta_capsule_id}:")
        print(f"  Integrity valid: {result['integrity_valid']}")
        print(f"  Archive valid: {result['archive_valid']}")
        print(f"  Ledger consistent: {result['ledger_consistent']}")

    elif args.command == "list":
        meta_capsules = creator.list_meta_capsules()
        print(f"All Meta-Capsules ({len(meta_capsules)}):")
        for mc in meta_capsules:
            print(
                f"  {mc['meta_capsule_id']}: {mc['created_at']} ({mc['systems_captured']} systems, {mc['files_captured']} files)"
            )

    elif args.command == "state":
        state = creator.capture_system_state()
        print(f"Current System State:")
        print(f"  Captured at: {state['captured_at']}")
        print(f"  Systems: {len(state['systems'])}")
        print(f"  Files: {len(state['file_hashes'])}")
        print(f"  State hash: {state['summary_stats']['state_hash']}")

        for system_name, system_data in state["systems"].items():
            print(
                f"    {system_name}: {type(system_data)} with {len(system_data) if isinstance(system_data, dict) else 'N/A'} entries"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
