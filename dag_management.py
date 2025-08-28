#!/usr/bin/env python3
"""
Directed Acyclic Graph (DAG) Management System
Creates mesh DAG base for task execution with fault-tolerant mechanisms
Integrates with EPOCH5 provenance tracking and agent management
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import random

# Optional NetworkX import for advanced graph validation
try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: NetworkX not available. Using basic DAG validation.")


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class DAGManager:
    def __init__(self, base_dir: str = "./archive/EPOCH5"):
        self.base_dir = Path(base_dir)
        self.dag_dir = self.base_dir / "dags"
        self.dag_dir.mkdir(parents=True, exist_ok=True)
        self.dags_file = self.dag_dir / "dags.json"
        self.execution_log = self.dag_dir / "execution.log"
        self.mesh_file = self.dag_dir / "mesh_base.json"

    def timestamp(self) -> str:
        """Generate ISO timestamp consistent with EPOCH5"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash consistent with EPOCH5"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def create_task(
        self,
        task_id: str,
        command: str,
        dependencies: List[str] = None,
        required_skills: List[str] = None,
        max_retries: int = 3,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """Create a task node for the DAG"""
        task = {
            "task_id": task_id,
            "command": command,
            "dependencies": dependencies or [],
            "required_skills": required_skills or [],
            "max_retries": max_retries,
            "timeout": timeout,
            "status": TaskStatus.PENDING.value,
            "created_at": self.timestamp(),
            "assigned_agent": None,
            "execution_attempts": 0,
            "execution_history": [],
            "output": None,
            "error": None,
            "hash": self.sha256(f"{task_id}|{command}|{','.join(dependencies or [])}"),
        }
        return task

    def create_dag(
        self, dag_id: str, tasks: List[Dict[str, Any]], description: str = ""
    ) -> Dict[str, Any]:
        """Create a new DAG with tasks"""
        # Validate DAG structure
        if not self.validate_dag(tasks):
            raise ValueError("DAG contains cycles or invalid dependencies")

        dag = {
            "dag_id": dag_id,
            "description": description,
            "tasks": {task["task_id"]: task for task in tasks},
            "created_at": self.timestamp(),
            "status": "created",
            "execution_stats": {
                "total_tasks": len(tasks),
                "completed_tasks": 0,
                "failed_tasks": 0,
                "retry_tasks": 0,
            },
            "mesh_nodes": self.generate_mesh_nodes(tasks),
            "hash": self.sha256(
                f"{dag_id}|{json.dumps([t['task_id'] for t in tasks], sort_keys=True)}"
            ),
        }
        return dag

    def validate_dag(self, tasks: List[Dict[str, Any]]) -> bool:
        """Validate that task dependencies form a valid DAG (no cycles)"""
        if HAS_NETWORKX:
            # Use NetworkX for comprehensive validation
            G = nx.DiGraph()

            # Add nodes
            for task in tasks:
                G.add_node(task["task_id"])

            # Add edges for dependencies
            for task in tasks:
                for dep in task["dependencies"]:
                    G.add_edge(dep, task["task_id"])

            # Check for cycles
            return nx.is_directed_acyclic_graph(G)
        else:
            # Basic validation without NetworkX
            return self.basic_dag_validation(tasks)

    def basic_dag_validation(self, tasks: List[Dict[str, Any]]) -> bool:
        """Basic DAG validation without NetworkX"""
        task_ids = {task["task_id"] for task in tasks}

        # Check that all dependencies exist
        for task in tasks:
            for dep in task["dependencies"]:
                if dep not in task_ids:
                    return False

        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(task_id, adjacency):
            visited.add(task_id)
            rec_stack.add(task_id)

            for neighbor in adjacency.get(task_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, adjacency):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        # Build adjacency list
        adjacency = {}
        for task in tasks:
            adjacency[task["task_id"]] = []
            for dep in task["dependencies"]:
                if dep not in adjacency:
                    adjacency[dep] = []
                adjacency[dep].append(task["task_id"])

        # Check for cycles
        for task_id in task_ids:
            if task_id not in visited:
                if has_cycle(task_id, adjacency):
                    return False

        return True

    def generate_mesh_nodes(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mesh connectivity for fault tolerance"""
        mesh_nodes = {}
        task_ids = [task["task_id"] for task in tasks]

        for task in tasks:
            # Create mesh connections for each task
            task_id = task["task_id"]

            # Primary connections (direct dependencies)
            primary_connections = task["dependencies"]

            # Secondary connections for fault tolerance (random subset of other tasks)
            other_tasks = [
                t for t in task_ids if t != task_id and t not in primary_connections
            ]
            secondary_connections = random.sample(other_tasks, min(2, len(other_tasks)))

            mesh_nodes[task_id] = {
                "primary_connections": primary_connections,
                "secondary_connections": secondary_connections,
                "mesh_id": self.sha256(f"{task_id}|mesh"),
                "fault_tolerance_level": len(secondary_connections) + 1,
            }

        return mesh_nodes

    def save_dag(self, dag: Dict[str, Any]) -> bool:
        """Save DAG to storage"""
        dags = self.load_dags()
        dags["dags"][dag["dag_id"]] = dag
        dags["last_updated"] = self.timestamp()

        with open(self.dags_file, "w") as f:
            json.dump(dags, f, indent=2)

        return True

    def load_dags(self) -> Dict[str, Any]:
        """Load DAGs from storage"""
        if self.dags_file.exists():
            with open(self.dags_file, "r") as f:
                return json.load(f)
        return {"dags": {}, "last_updated": self.timestamp()}

    def get_ready_tasks(self, dag_id: str) -> List[Dict[str, Any]]:
        """Get tasks that are ready to execute (dependencies completed)"""
        dags = self.load_dags()
        if dag_id not in dags["dags"]:
            return []

        dag = dags["dags"][dag_id]
        ready_tasks = []

        for task_id, task in dag["tasks"].items():
            if task["status"] != TaskStatus.PENDING.value:
                continue

            # Check if all dependencies are completed
            dependencies_completed = all(
                dag["tasks"][dep_id]["status"] == TaskStatus.COMPLETED.value
                for dep_id in task["dependencies"]
                if dep_id in dag["tasks"]
            )

            if dependencies_completed:
                ready_tasks.append(task)

        return ready_tasks

    def assign_task(self, dag_id: str, task_id: str, agent_did: str) -> bool:
        """Assign a task to an agent"""
        dags = self.load_dags()
        if dag_id not in dags["dags"] or task_id not in dags["dags"][dag_id]["tasks"]:
            return False

        task = dags["dags"][dag_id]["tasks"][task_id]
        task["assigned_agent"] = agent_did
        task["status"] = TaskStatus.RUNNING.value
        task["execution_attempts"] += 1
        task["execution_history"].append(
            {
                "attempt": task["execution_attempts"],
                "agent": agent_did,
                "started_at": self.timestamp(),
                "status": "started",
            }
        )

        self.save_dag(dags["dags"][dag_id])
        self.log_execution(dag_id, task_id, "TASK_ASSIGNED", {"agent": agent_did})

        return True

    def complete_task(
        self, dag_id: str, task_id: str, output: str = None, success: bool = True
    ) -> bool:
        """Mark a task as completed or failed"""
        dags = self.load_dags()
        if dag_id not in dags["dags"] or task_id not in dags["dags"][dag_id]["tasks"]:
            return False

        dag = dags["dags"][dag_id]
        task = dag["tasks"][task_id]

        if success:
            task["status"] = TaskStatus.COMPLETED.value
            task["output"] = output
            dag["execution_stats"]["completed_tasks"] += 1
            self.log_execution(
                dag_id, task_id, "TASK_COMPLETED", {"output_length": len(output or "")}
            )
        else:
            if task["execution_attempts"] >= task["max_retries"]:
                task["status"] = TaskStatus.FAILED.value
                dag["execution_stats"]["failed_tasks"] += 1
                self.log_execution(
                    dag_id,
                    task_id,
                    "TASK_FAILED",
                    {"attempts": task["execution_attempts"]},
                )
            else:
                task["status"] = TaskStatus.RETRYING.value
                dag["execution_stats"]["retry_tasks"] += 1
                self.log_execution(
                    dag_id,
                    task_id,
                    "TASK_RETRY",
                    {"attempt": task["execution_attempts"]},
                )

        # Update execution history
        if task["execution_history"]:
            task["execution_history"][-1]["completed_at"] = self.timestamp()
            task["execution_history"][-1]["status"] = (
                "completed" if success else "failed"
            )

        self.save_dag(dag)
        return True

    def execute_dag(self, dag_id: str, simulation: bool = True) -> Dict[str, Any]:
        """Execute a DAG with fault-tolerant mechanisms"""
        dags = self.load_dags()
        if dag_id not in dags["dags"]:
            return {"error": "DAG not found"}

        dag = dags["dags"][dag_id]
        dag["status"] = "executing"

        execution_result = {
            "dag_id": dag_id,
            "started_at": self.timestamp(),
            "simulation": simulation,
            "completed_tasks": [],
            "failed_tasks": [],
            "execution_order": [],
        }

        # Simulate execution or perform real execution
        max_iterations = len(dag["tasks"]) * 2  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            ready_tasks = self.get_ready_tasks(dag_id)

            if not ready_tasks:
                # Check if all tasks are completed or failed
                remaining_tasks = [
                    t
                    for t in dag["tasks"].values()
                    if t["status"]
                    in [
                        TaskStatus.PENDING.value,
                        TaskStatus.RUNNING.value,
                        TaskStatus.RETRYING.value,
                    ]
                ]
                if not remaining_tasks:
                    break

            for task in ready_tasks:
                task_id = task["task_id"]
                execution_result["execution_order"].append(task_id)

                if simulation:
                    # Simulate task execution
                    success = random.choice(
                        [True, True, True, False]
                    )  # 75% success rate
                    self.assign_task(
                        dag_id, task_id, f"simulated_agent_{random.randint(1, 5)}"
                    )
                    self.complete_task(
                        dag_id, task_id, f"simulated_output_{task_id}", success
                    )

                    if success:
                        execution_result["completed_tasks"].append(task_id)
                    else:
                        execution_result["failed_tasks"].append(task_id)
                else:
                    # Real execution would require agent integration
                    self.log_execution(
                        dag_id, task_id, "TASK_READY", {"simulation": False}
                    )

            iteration += 1

        # Update final DAG status
        dag = dags["dags"][dag_id]
        completed_count = dag["execution_stats"]["completed_tasks"]
        total_count = dag["execution_stats"]["total_tasks"]

        if completed_count == total_count:
            dag["status"] = "completed"
        elif dag["execution_stats"]["failed_tasks"] > 0:
            dag["status"] = "partial_failure"
        else:
            dag["status"] = "executing"

        execution_result["completed_at"] = self.timestamp()
        execution_result["final_status"] = dag["status"]

        self.save_dag(dag)
        self.log_execution(dag_id, "DAG", "EXECUTION_COMPLETED", execution_result)

        return execution_result

    def log_execution(
        self, dag_id: str, task_id: str, event: str, data: Dict[str, Any]
    ):
        """Log execution events with EPOCH5 compatible format"""
        log_entry = {
            "timestamp": self.timestamp(),
            "dag_id": dag_id,
            "task_id": task_id,
            "event": event,
            "data": data,
            "hash": self.sha256(f"{self.timestamp()}|{dag_id}|{task_id}|{event}"),
        }

        with open(self.execution_log, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")

    def get_dag_status(self, dag_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a DAG"""
        dags = self.load_dags()
        if dag_id not in dags["dags"]:
            return None

        dag = dags["dags"][dag_id]
        return {
            "dag_id": dag_id,
            "status": dag["status"],
            "execution_stats": dag["execution_stats"],
            "total_tasks": len(dag["tasks"]),
            "created_at": dag["created_at"],
        }


# CLI interface for DAG management
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 DAG Management System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create DAG
    create_parser = subparsers.add_parser("create", help="Create a new DAG")
    create_parser.add_argument("dag_id", help="DAG identifier")
    create_parser.add_argument(
        "tasks_file", help="JSON file containing task definitions"
    )

    # Execute DAG
    execute_parser = subparsers.add_parser("execute", help="Execute a DAG")
    execute_parser.add_argument("dag_id", help="DAG to execute")
    execute_parser.add_argument(
        "--real", action="store_true", help="Real execution (not simulation)"
    )

    # Status
    status_parser = subparsers.add_parser("status", help="Get DAG status")
    status_parser.add_argument("dag_id", help="DAG identifier")

    # List DAGs
    subparsers.add_parser("list", help="List all DAGs")

    args = parser.parse_args()
    manager = DAGManager()

    if args.command == "create":
        with open(args.tasks_file, "r") as f:
            tasks_data = json.load(f)

        tasks = [manager.create_task(**task_def) for task_def in tasks_data["tasks"]]
        dag = manager.create_dag(args.dag_id, tasks, tasks_data.get("description", ""))
        manager.save_dag(dag)
        print(f"Created DAG: {dag['dag_id']} with {len(tasks)} tasks")

    elif args.command == "execute":
        result = manager.execute_dag(args.dag_id, simulation=not args.real)
        print(f"DAG execution result: {result['final_status']}")
        print(
            f"Completed: {len(result['completed_tasks'])}, Failed: {len(result['failed_tasks'])}"
        )

    elif args.command == "status":
        status = manager.get_dag_status(args.dag_id)
        if status:
            print(f"DAG {args.dag_id}: {status['status']}")
            print(f"Tasks: {status['execution_stats']}")
        else:
            print(f"DAG {args.dag_id} not found")

    elif args.command == "list":
        dags = manager.load_dags()
        print(f"All DAGs ({len(dags['dags'])}):")
        for dag_id, dag in dags["dags"].items():
            print(
                f"  {dag_id}: {dag['status']} ({dag['execution_stats']['completed_tasks']}/{dag['execution_stats']['total_tasks']} tasks)"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
