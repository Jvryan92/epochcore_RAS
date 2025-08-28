#!/usr/bin/env python3
"""
Cycle Execution System - Implements cycles with budget control, latency tracking, and task assignments
Includes SLA metrics and PBFT consensus for each cycle execution
Integrates with EPOCH5 provenance tracking and DAG management
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random
from strategy_ethical import EthicalEngine, EthicalAssessment
from ethical_reflection import EthicalReflectionEngine

# Import the ceiling manager for dynamic ceiling support
try:
    from ceiling_manager import CeilingManager, ServiceTier, CeilingType

    CEILING_MANAGER_AVAILABLE = True
except ImportError:
    CEILING_MANAGER_AVAILABLE = False


class CycleStatus(Enum):
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONSENSUS_PENDING = "consensus_pending"


class PBFTPhase(Enum):
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"


class CycleExecutor:
    def __init__(self, base_dir: str = "./archive/EPOCH5"):
        self.base_dir = Path(base_dir)
        self.cycles_dir = self.base_dir / "cycles"
        self.cycles_dir.mkdir(parents=True, exist_ok=True)
        self.cycles_file = self.cycles_dir / "cycles.json"
        self.execution_log = self.cycles_dir / "cycle_execution.log"
        self.sla_metrics_file = self.cycles_dir / "sla_metrics.json"
        self.consensus_log = self.cycles_dir / "pbft_consensus.log"
        
        # Initialize ethical components
        self.ethical_dir = self.cycles_dir / "ethical"
        self.ethical_dir.mkdir(parents=True, exist_ok=True)
        self.ethical_engine = EthicalEngine(str(self.ethical_dir))
        self.ethical_reflection = EthicalReflectionEngine(str(self.ethical_dir / "reflection"))

        # Initialize ceiling manager for dynamic ceiling support
        if CEILING_MANAGER_AVAILABLE:
            self.ceiling_manager = CeilingManager(base_dir)
        else:
            self.ceiling_manager = None

    def timestamp(self) -> str:
        """Generate ISO timestamp consistent with EPOCH5"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash consistent with EPOCH5"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def create_cycle(
        self,
        cycle_id: str,
        budget: float,
        max_latency: float,
        task_assignments: List[Dict[str, Any]],
        sla_requirements: Dict[str, Any] = None,
        service_tier: str = "freemium",
        ceiling_config_id: str = None,
        ethical_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new execution cycle with dynamic ceiling support"""

        # Apply dynamic ceiling adjustments if ceiling manager is available
        effective_budget = budget
        effective_max_latency = max_latency

        # Perform ethical assessment before cycle creation
        ethical_assessment = self.ethical_engine.assess_action(
            action_id=f"cycle_{cycle_id}",
            context={
                "cycle_id": cycle_id,
                "budget": budget,
                "max_latency": max_latency,
                "task_count": len(task_assignments),
                "service_tier": service_tier,
                "ethical_constraints": ethical_constraints
            }
        )
        
        if not ethical_assessment.constraints_satisfied:
            self.log_execution(
                cycle_id,
                "ETHICAL_ASSESSMENT_FAILED",
                {
                    "reasoning": ethical_assessment.reasoning,
                    "scores": ethical_assessment.scores,
                    "timestamp": self.timestamp()
                }
            )
            raise ValueError(f"Cycle creation failed ethical assessment: {', '.join(ethical_assessment.reasoning)}")
            
        # Predict potential impact
        impact = self.ethical_engine.predict_impact(
            action_id=f"cycle_{cycle_id}",
            context={
                "budget": budget,
                "task_assignments": task_assignments,
                "service_tier": service_tier
            }
        )
        
        if impact.uncertainty > 0.8:
            self.log_execution(
                cycle_id,
                "HIGH_IMPACT_UNCERTAINTY",
                {
                    "uncertainty": impact.uncertainty,
                    "stakeholders": impact.stakeholders,
                    "timestamp": self.timestamp()
                }
            )
        
        if self.ceiling_manager and ceiling_config_id:
            try:
                tier = ServiceTier(service_tier)
                effective_budget = self.ceiling_manager.get_effective_ceiling(
                    ceiling_config_id, CeilingType.BUDGET
                )
                effective_max_latency = self.ceiling_manager.get_effective_ceiling(
                    ceiling_config_id, CeilingType.LATENCY
                )

                # Log ceiling application
                self.log_execution(
                    cycle_id,
                    "DYNAMIC_CEILING_APPLIED",
                    {
                        "original_budget": budget,
                        "effective_budget": effective_budget,
                        "original_max_latency": max_latency,
                        "effective_max_latency": effective_max_latency,
                        "service_tier": service_tier,
                        "ceiling_config_id": ceiling_config_id,
                        "ethical_assessment": {
                            "score": ethical_assessment.overall_score,
                            "impact_uncertainty": impact.uncertainty
                        },
                    },
                )
            except Exception as e:
                self.log_execution(
                    cycle_id, "CEILING_APPLICATION_ERROR", {"error": str(e)}
                )
                # Fall back to original values
                effective_budget = budget
                effective_max_latency = max_latency

        cycle = {
            "cycle_id": cycle_id,
            "budget": effective_budget,
            "original_budget": budget,  # Keep track of original for analysis
            "spent_budget": 0.0,
            "max_latency": effective_max_latency,
            "original_max_latency": max_latency,  # Keep track of original for analysis
            "actual_latency": 0.0,
            "task_assignments": task_assignments,
            "service_tier": service_tier,
            "ceiling_config_id": ceiling_config_id,
            "sla_requirements": sla_requirements
            or {
                "min_success_rate": 0.95,
                "max_failure_rate": 0.05,
                "max_retry_count": 3,
            },
            "created_at": self.timestamp(),
            "started_at": None,
            "completed_at": None,
            "status": CycleStatus.PLANNED.value,
            "consensus_state": {
                "phase": None,
                "votes": {},
                "committed": False,
                "validator_nodes": [],
            },
            "execution_metrics": {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "total_tasks": len(task_assignments),
                "success_rate": 0.0,
                "average_task_latency": 0.0,
            },
            "resource_usage": {"cpu_time": 0.0, "memory_peak": 0.0, "network_io": 0.0},
            "hash": self.sha256(
                f"{cycle_id}|{budget}|{max_latency}|{len(task_assignments)}"
            ),
        }
        return cycle

    def save_cycle(self, cycle: Dict[str, Any]) -> bool:
        """Save cycle to storage"""
        cycles = self.load_cycles()
        cycles["cycles"][cycle["cycle_id"]] = cycle
        cycles["last_updated"] = self.timestamp()

        with open(self.cycles_file, "w") as f:
            json.dump(cycles, f, indent=2)

        return True

    def load_cycles(self) -> Dict[str, Any]:
        """Load cycles from storage"""
        if self.cycles_file.exists():
            with open(self.cycles_file, "r") as f:
                return json.load(f)
        return {"cycles": {}, "last_updated": self.timestamp()}

    def start_cycle(self, cycle_id: str, validator_nodes: List[str]) -> bool:
        """Start executing a cycle with PBFT consensus initialization"""
        cycles = self.load_cycles()
        if cycle_id not in cycles["cycles"]:
            return False

        cycle = cycles["cycles"][cycle_id]
        if cycle["status"] != CycleStatus.PLANNED.value:
            return False

        cycle["started_at"] = self.timestamp()
        cycle["status"] = CycleStatus.EXECUTING.value
        cycle["consensus_state"]["validator_nodes"] = validator_nodes
        cycle["consensus_state"]["phase"] = PBFTPhase.PRE_PREPARE.value

        self.save_cycle(cycle)
        self.log_execution(
            cycle_id,
            "CYCLE_STARTED",
            {
                "validators": len(validator_nodes),
                "tasks": cycle["execution_metrics"]["total_tasks"],
            },
        )

        # Initialize PBFT consensus
        self.initiate_pbft_consensus(
            cycle_id, "cycle_start", {"action": "start_execution"}
        )

        return True

    def execute_task_assignment(
        self, cycle_id: str, assignment_index: int, simulation: bool = True
    ) -> Dict[str, Any]:
        """Execute a single task assignment within a cycle"""
        cycles = self.load_cycles()
        if cycle_id not in cycles["cycles"]:
            return {"error": "Cycle not found"}

        cycle = cycles["cycles"][cycle_id]
        if assignment_index >= len(cycle["task_assignments"]):
            return {"error": "Invalid assignment index"}

        assignment = cycle["task_assignments"][assignment_index]
        start_time = time.time()

        result = {
            "assignment_index": assignment_index,
            "task_id": assignment.get("task_id", f"task_{assignment_index}"),
            "agent_did": assignment.get("agent_did"),
            "started_at": self.timestamp(),
            "success": False,
            "output": None,
            "error": None,
            "latency": 0.0,
            "cost": 0.0,
        }

        if simulation:
            # Simulate task execution
            execution_time = random.uniform(0.1, 2.0)  # Random execution time
            time.sleep(execution_time)  # Simulate actual work

            success_probability = 0.85  # 85% success rate
            result["success"] = random.random() < success_probability
            result["latency"] = execution_time
            result["cost"] = execution_time * random.uniform(
                0.1, 1.0
            )  # Cost based on time

            if result["success"]:
                result["output"] = (
                    f"Simulated successful execution of {result['task_id']}"
                )
            else:
                result["error"] = f"Simulated failure in {result['task_id']}"
        else:
            # Real execution would integrate with agent system
            result["error"] = (
                "Real execution not implemented - requires agent integration"
            )

        result["completed_at"] = self.timestamp()

        # Update cycle metrics
        cycle["spent_budget"] += result["cost"]
        cycle["actual_latency"] += result["latency"]

        if result["success"]:
            cycle["execution_metrics"]["tasks_completed"] += 1
        else:
            cycle["execution_metrics"]["tasks_failed"] += 1

        # Update success rate
        total_executed = (
            cycle["execution_metrics"]["tasks_completed"]
            + cycle["execution_metrics"]["tasks_failed"]
        )
        if total_executed > 0:
            cycle["execution_metrics"]["success_rate"] = (
                cycle["execution_metrics"]["tasks_completed"] / total_executed
            )
            cycle["execution_metrics"]["average_task_latency"] = (
                cycle["actual_latency"] / total_executed
            )

        self.save_cycle(cycle)
        self.log_execution(cycle_id, "TASK_EXECUTED", result)

        return result

    def check_sla_compliance(self, cycle_id: str) -> Dict[str, Any]:
        """Check if cycle meets SLA requirements"""
        cycles = self.load_cycles()
        if cycle_id not in cycles["cycles"]:
            return {"error": "Cycle not found"}

        cycle = cycles["cycles"][cycle_id]
        sla_req = cycle["sla_requirements"]
        metrics = cycle["execution_metrics"]

        sla_status = {
            "cycle_id": cycle_id,
            "checked_at": self.timestamp(),
            "compliant": True,
            "violations": [],
            "metrics": {
                "success_rate": metrics["success_rate"],
                "required_success_rate": sla_req["min_success_rate"],
                "budget_usage": (
                    cycle["spent_budget"] / cycle["budget"]
                    if cycle["budget"] > 0
                    else 0
                ),
                "latency_usage": (
                    cycle["actual_latency"] / cycle["max_latency"]
                    if cycle["max_latency"] > 0
                    else 0
                ),
            },
        }

        # Check success rate
        if metrics["success_rate"] < sla_req["min_success_rate"]:
            sla_status["violations"].append(
                {
                    "type": "success_rate",
                    "required": sla_req["min_success_rate"],
                    "actual": metrics["success_rate"],
                }
            )
            sla_status["compliant"] = False

        # Check budget
        if cycle["spent_budget"] > cycle["budget"]:
            sla_status["violations"].append(
                {
                    "type": "budget_exceeded",
                    "budget": cycle["budget"],
                    "spent": cycle["spent_budget"],
                }
            )
            sla_status["compliant"] = False

        # Check latency
        if cycle["actual_latency"] > cycle["max_latency"]:
            sla_status["violations"].append(
                {
                    "type": "latency_exceeded",
                    "max_latency": cycle["max_latency"],
                    "actual_latency": cycle["actual_latency"],
                }
            )
            sla_status["compliant"] = False

        # Save SLA metrics
        self.save_sla_metrics(sla_status)

        # Update ceiling configuration if available
        if self.ceiling_manager and cycle.get("ceiling_config_id"):
            try:
                performance_metrics = {
                    "success_rate": metrics["success_rate"],
                    "actual_latency": cycle["actual_latency"],
                    "spent_budget": cycle["spent_budget"],
                    "sla_compliant": sla_status["compliant"],
                }

                self.ceiling_manager.adjust_ceiling_for_performance(
                    cycle["ceiling_config_id"], performance_metrics
                )

                # Generate upgrade recommendations
                upgrade_rec = self.ceiling_manager.get_upgrade_recommendations(
                    cycle["ceiling_config_id"]
                )
                sla_status["upgrade_recommendation"] = upgrade_rec

            except Exception as e:
                sla_status["ceiling_update_error"] = str(e)

        return sla_status

    def initiate_pbft_consensus(
        self, cycle_id: str, decision_type: str, proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize PBFT consensus for cycle decisions"""
        cycles = self.load_cycles()
        if cycle_id not in cycles["cycles"]:
            return {"error": "Cycle not found"}

        cycle = cycles["cycles"][cycle_id]
        validators = cycle["consensus_state"]["validator_nodes"]

        consensus_request = {
            "cycle_id": cycle_id,
            "decision_type": decision_type,
            "proposal": proposal,
            "initiated_at": self.timestamp(),
            "phase": PBFTPhase.PRE_PREPARE.value,
            "sequence_number": len(cycle["consensus_state"]["votes"]) + 1,
            "votes": {"pre_prepare": {}, "prepare": {}, "commit": {}},
            "required_votes": (2 * len(validators)) // 3
            + 1,  # Byzantine fault tolerance
            "hash": self.sha256(
                f"{cycle_id}|{decision_type}|{json.dumps(proposal, sort_keys=True)}"
            ),
        }

        # Simulate validator votes (in real implementation, this would be distributed)
        if len(validators) > 0:
            self.simulate_pbft_voting(consensus_request, validators)

        # Update cycle consensus state
        cycle["consensus_state"]["phase"] = consensus_request["phase"]
        cycle["consensus_state"]["votes"][
            consensus_request["sequence_number"]
        ] = consensus_request

        self.save_cycle(cycle)
        self.log_consensus(consensus_request)

        return consensus_request

    def simulate_pbft_voting(
        self, consensus_request: Dict[str, Any], validators: List[str]
    ):
        """Simulate PBFT voting process"""
        required_votes = consensus_request["required_votes"]

        # Pre-prepare phase
        for validator in validators:
            if random.random() > 0.1:  # 90% participation rate
                consensus_request["votes"]["pre_prepare"][validator] = {
                    "vote": "accept",
                    "timestamp": self.timestamp(),
                    "signature": self.sha256(
                        f"pre_prepare|{validator}|{consensus_request['hash']}"
                    ),
                }

        # Check if pre-prepare threshold is met
        if len(consensus_request["votes"]["pre_prepare"]) >= required_votes:
            consensus_request["phase"] = PBFTPhase.PREPARE.value

            # Prepare phase
            for validator in validators:
                if random.random() > 0.05:  # 95% participation rate
                    consensus_request["votes"]["prepare"][validator] = {
                        "vote": "accept",
                        "timestamp": self.timestamp(),
                        "signature": self.sha256(
                            f"prepare|{validator}|{consensus_request['hash']}"
                        ),
                    }

            # Check if prepare threshold is met
            if len(consensus_request["votes"]["prepare"]) >= required_votes:
                consensus_request["phase"] = PBFTPhase.COMMIT.value

                # Commit phase
                for validator in validators:
                    if random.random() > 0.02:  # 98% participation rate
                        consensus_request["votes"]["commit"][validator] = {
                            "vote": "accept",
                            "timestamp": self.timestamp(),
                            "signature": self.sha256(
                                f"commit|{validator}|{consensus_request['hash']}"
                            ),
                        }

                # Check if commit threshold is met
                if len(consensus_request["votes"]["commit"]) >= required_votes:
                    consensus_request["committed"] = True
                    consensus_request["committed_at"] = self.timestamp()

    def complete_cycle(self, cycle_id: str, force: bool = False) -> bool:
        """Complete a cycle execution with final consensus"""
        cycles = self.load_cycles()
        if cycle_id not in cycles["cycles"]:
            return False

        cycle = cycles["cycles"][cycle_id]

        if not force and cycle["status"] != CycleStatus.EXECUTING.value:
            return False

        cycle["completed_at"] = self.timestamp()

        # Check SLA compliance
        sla_status = self.check_sla_compliance(cycle_id)

        # Final consensus on cycle completion
        completion_proposal = {
            "action": "complete_cycle",
            "sla_compliant": sla_status["compliant"],
            "final_metrics": cycle["execution_metrics"],
        }

        consensus_result = self.initiate_pbft_consensus(
            cycle_id, "cycle_completion", completion_proposal
        )

        if consensus_result.get("committed", False) or force:
            cycle["status"] = CycleStatus.COMPLETED.value
        else:
            cycle["status"] = CycleStatus.CONSENSUS_PENDING.value

        self.save_cycle(cycle)
        self.log_execution(
            cycle_id,
            "CYCLE_COMPLETED",
            {
                "status": cycle["status"],
                "sla_compliant": sla_status["compliant"],
                "consensus_committed": consensus_result.get("committed", False),
            },
        )

        return True

    def execute_full_cycle(
        self, cycle_id: str, validator_nodes: List[str], simulation: bool = True
    ) -> Dict[str, Any]:
        """Execute a complete cycle from start to finish"""
        # Start the cycle
        if not self.start_cycle(cycle_id, validator_nodes):
            return {"error": "Failed to start cycle"}

        cycles = self.load_cycles()
        cycle = cycles["cycles"][cycle_id]

        execution_results = []

        # Execute all task assignments
        for i in range(len(cycle["task_assignments"])):
            result = self.execute_task_assignment(cycle_id, i, simulation)
            execution_results.append(result)

            # Check budget and latency constraints
            cycles = self.load_cycles()  # Refresh cycle data
            cycle = cycles["cycles"][cycle_id]

            if cycle["spent_budget"] > cycle["budget"]:
                self.log_execution(
                    cycle_id,
                    "BUDGET_EXCEEDED",
                    {"budget": cycle["budget"], "spent": cycle["spent_budget"]},
                )
                break

            if cycle["actual_latency"] > cycle["max_latency"]:
                self.log_execution(
                    cycle_id,
                    "LATENCY_EXCEEDED",
                    {"max": cycle["max_latency"], "actual": cycle["actual_latency"]},
                )
                break

        # Complete the cycle
        self.complete_cycle(cycle_id)

        cycles = self.load_cycles()
        final_cycle = cycles["cycles"][cycle_id]

        return {
            "cycle_id": cycle_id,
            "status": final_cycle["status"],
            "execution_results": execution_results,
            "final_metrics": final_cycle["execution_metrics"],
            "sla_compliance": self.check_sla_compliance(cycle_id),
            "resource_usage": final_cycle["resource_usage"],
        }

    def log_execution(self, cycle_id: str, event: str, data: Dict[str, Any]):
        """Log execution events with EPOCH5 compatible format"""
        log_entry = {
            "timestamp": self.timestamp(),
            "cycle_id": cycle_id,
            "event": event,
            "data": data,
            "hash": self.sha256(f"{self.timestamp()}|{cycle_id}|{event}"),
        }

        with open(self.execution_log, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")

    def log_consensus(self, consensus_request: Dict[str, Any]):
        """Log PBFT consensus events"""
        log_entry = {
            "timestamp": self.timestamp(),
            "consensus_request": consensus_request,
            "hash": self.sha256(f"{self.timestamp()}|{consensus_request['hash']}"),
        }

        with open(self.consensus_log, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")

    def save_sla_metrics(self, sla_status: Dict[str, Any]):
        """Save SLA metrics for reporting"""
        if self.sla_metrics_file.exists():
            with open(self.sla_metrics_file, "r") as f:
                metrics = json.load(f)
        else:
            metrics = {"sla_reports": [], "last_updated": self.timestamp()}

        metrics["sla_reports"].append(sla_status)
        metrics["last_updated"] = self.timestamp()

        with open(self.sla_metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)


# CLI interface for cycle execution
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 Cycle Execution System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create cycle
    create_parser = subparsers.add_parser("create", help="Create a new cycle")
    create_parser.add_argument("cycle_id", help="Cycle identifier")
    create_parser.add_argument("budget", type=float, help="Budget limit")
    create_parser.add_argument("max_latency", type=float, help="Maximum latency")
    create_parser.add_argument(
        "assignments_file", help="JSON file with task assignments"
    )

    # Execute cycle
    execute_parser = subparsers.add_parser("execute", help="Execute a cycle")
    execute_parser.add_argument("cycle_id", help="Cycle to execute")
    execute_parser.add_argument(
        "--validators",
        nargs="+",
        default=["validator1", "validator2", "validator3"],
        help="Validator nodes",
    )
    execute_parser.add_argument(
        "--real", action="store_true", help="Real execution (not simulation)"
    )

    # Status
    status_parser = subparsers.add_parser("status", help="Get cycle status")
    status_parser.add_argument("cycle_id", help="Cycle identifier")

    # SLA check
    sla_parser = subparsers.add_parser("sla", help="Check SLA compliance")
    sla_parser.add_argument("cycle_id", help="Cycle identifier")

    # List cycles
    subparsers.add_parser("list", help="List all cycles")

    args = parser.parse_args()
    executor = CycleExecutor()

    if args.command == "create":
        with open(args.assignments_file, "r") as f:
            assignments_data = json.load(f)

        cycle = executor.create_cycle(
            args.cycle_id,
            args.budget,
            args.max_latency,
            assignments_data["assignments"],
            assignments_data.get("sla_requirements"),
        )
        executor.save_cycle(cycle)
        print(
            f"Created cycle: {cycle['cycle_id']} with {len(cycle['task_assignments'])} tasks"
        )

    elif args.command == "execute":
        result = executor.execute_full_cycle(
            args.cycle_id, args.validators, simulation=not args.real
        )
        print(f"Cycle execution result: {result['status']}")
        print(f"SLA Compliant: {result['sla_compliance']['compliant']}")
        print(f"Success Rate: {result['final_metrics']['success_rate']:.2f}")

    elif args.command == "status":
        cycles = executor.load_cycles()
        if args.cycle_id in cycles["cycles"]:
            cycle = cycles["cycles"][args.cycle_id]
            print(f"Cycle {args.cycle_id}: {cycle['status']}")
            print(f"Budget: {cycle['spent_budget']:.2f}/{cycle['budget']:.2f}")
            print(
                f"Tasks: {cycle['execution_metrics']['tasks_completed']}/{cycle['execution_metrics']['total_tasks']}"
            )
        else:
            print(f"Cycle {args.cycle_id} not found")

    elif args.command == "sla":
        sla_status = executor.check_sla_compliance(args.cycle_id)
        print(
            f"SLA Compliance for {args.cycle_id}: {'PASS' if sla_status['compliant'] else 'FAIL'}"
        )
        if sla_status["violations"]:
            print("Violations:")
            for violation in sla_status["violations"]:
                print(f"  - {violation['type']}: {violation}")

    elif args.command == "list":
        cycles = executor.load_cycles()
        print(f"All Cycles ({len(cycles['cycles'])}):")
        for cycle_id, cycle in cycles["cycles"].items():
            print(
                f"  {cycle_id}: {cycle['status']} (budget: {cycle['spent_budget']:.2f}/{cycle['budget']:.2f})"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
