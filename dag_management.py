#!/usr/bin/env python3
"""
EpochCore RAS DAG (Directed Acyclic Graph) Management System

Manages workflow execution, optimization, and recursive improvement.
Includes hooks for autonomous workflow enhancement and bottleneck resolution.
"""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from recursive_improvement import ImprovementStrategy, SubsystemHook, get_framework


class TaskStatus(Enum):
    """Status of a task in the DAG."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Task:
    """Represents a task node in the DAG."""
    
    def __init__(self, task_id: str, name: str, dependencies: List[str] = None,
                 estimated_duration: int = 60, priority: int = 1):
        self.id = task_id
        self.name = name
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.estimated_duration = estimated_duration  # seconds
        self.actual_duration = 0
        self.priority = priority
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.retry_count = 0
        self.max_retries = 3
        
    def to_dict(self) -> Dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "priority": self.priority,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }


class WorkflowDAG:
    """Represents a complete workflow as a directed acyclic graph."""
    
    def __init__(self, dag_id: str, name: str):
        self.id = dag_id
        self.name = name
        self.tasks = {}
        self.execution_history = []
        self.created_at = datetime.now()
        self.last_execution = None
        self.success_rate = 1.0
        self.avg_execution_time = 0
        
    def add_task(self, task: Task) -> None:
        """Add a task to the DAG."""
        self.tasks[task.id] = task
        
    def get_executable_tasks(self) -> List[Task]:
        """Get tasks that can be executed (all dependencies completed)."""
        executable = []
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                all(self.tasks[dep_id].status == TaskStatus.COMPLETED 
                    for dep_id in task.dependencies if dep_id in self.tasks)):
                executable.append(task)
        return sorted(executable, key=lambda t: t.priority, reverse=True)
        
    def is_complete(self) -> bool:
        """Check if the entire DAG is complete."""
        return all(task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED] 
                  for task in self.tasks.values())
        
    def has_failed(self) -> bool:
        """Check if the DAG has failed."""
        return any(task.status == TaskStatus.FAILED and task.retry_count >= task.max_retries
                  for task in self.tasks.values())
        
    def to_dict(self) -> Dict:
        """Convert DAG to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
            "created_at": self.created_at.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "is_complete": self.is_complete(),
            "has_failed": self.has_failed()
        }


class DAGManager:
    """Manager for DAG workflows and execution."""
    
    def __init__(self):
        self.workflows = {}
        self.execution_queue = []
        self.running_workflows = {}
        self.execution_history = []
        
        # Initialize with sample workflows
        self._initialize_sample_workflows()
        
    def _initialize_sample_workflows(self):
        """Initialize with sample workflows for demonstration."""
        # Sample workflow 1: Data processing pipeline
        dag1 = WorkflowDAG("dag_001", "Data Processing Pipeline")
        dag1.add_task(Task("task_001", "Extract Data", [], 30, 3))
        dag1.add_task(Task("task_002", "Transform Data", ["task_001"], 60, 2))
        dag1.add_task(Task("task_003", "Validate Data", ["task_002"], 45, 2))
        dag1.add_task(Task("task_004", "Load Data", ["task_003"], 90, 1))
        
        # Sample workflow 2: ML training pipeline
        dag2 = WorkflowDAG("dag_002", "ML Training Pipeline")
        dag2.add_task(Task("task_101", "Prepare Dataset", [], 120, 3))
        dag2.add_task(Task("task_102", "Feature Engineering", ["task_101"], 180, 2))
        dag2.add_task(Task("task_103", "Train Model", ["task_102"], 300, 1))
        dag2.add_task(Task("task_104", "Validate Model", ["task_103"], 60, 1))
        dag2.add_task(Task("task_105", "Deploy Model", ["task_104"], 45, 1))
        
        # Simulate some execution history
        dag1.success_rate = 0.92
        dag1.avg_execution_time = 225
        dag1.last_execution = datetime.now() - timedelta(hours=2)
        
        dag2.success_rate = 0.85
        dag2.avg_execution_time = 705
        dag2.last_execution = datetime.now() - timedelta(hours=6)
        
        self.workflows[dag1.id] = dag1
        self.workflows[dag2.id] = dag2
        
    def create_workflow(self, name: str) -> WorkflowDAG:
        """Create a new workflow DAG."""
        dag_id = str(uuid.uuid4())
        dag = WorkflowDAG(dag_id, name)
        self.workflows[dag_id] = dag
        return dag
        
    def get_workflow(self, dag_id: str) -> Optional[WorkflowDAG]:
        """Get workflow by ID."""
        return self.workflows.get(dag_id)
        
    def execute_workflow(self, dag_id: str) -> Dict:
        """Execute a workflow (simulated)."""
        if dag_id not in self.workflows:
            return {"status": "error", "message": f"Workflow {dag_id} not found"}
            
        dag = self.workflows[dag_id]
        
        # Simulate execution
        start_time = datetime.now()
        
        # Reset task statuses
        for task in dag.tasks.values():
            task.status = TaskStatus.PENDING
            task.start_time = None
            task.end_time = None
            task.actual_duration = 0
            
        # Simulate task execution
        total_duration = 0
        for task in dag.tasks.values():
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
            # Simulate work
            time.sleep(0.1)  # Brief pause for simulation
            
            # Random chance of task failure (10%)
            import random
            if random.random() < 0.1:
                task.status = TaskStatus.FAILED
                task.error_message = "Simulated task failure"
            else:
                task.status = TaskStatus.COMPLETED
                
            task.end_time = datetime.now()
            task.actual_duration = int((task.end_time - task.start_time).total_seconds())
            total_duration += task.actual_duration
            
        end_time = datetime.now()
        execution_time = int((end_time - start_time).total_seconds())
        
        # Update DAG statistics
        dag.last_execution = end_time
        dag.execution_history.append({
            "timestamp": end_time.isoformat(),
            "duration": execution_time,
            "success": not dag.has_failed()
        })
        
        # Update success rate
        recent_executions = dag.execution_history[-10:]  # Last 10 executions
        successful = sum(1 for ex in recent_executions if ex["success"])
        dag.success_rate = successful / len(recent_executions) if recent_executions else 1.0
        
        # Update average execution time
        if recent_executions:
            dag.avg_execution_time = sum(ex["duration"] for ex in recent_executions) / len(recent_executions)
        
        return {
            "status": "success" if not dag.has_failed() else "failed",
            "dag_id": dag_id,
            "execution_time": execution_time,
            "tasks_completed": sum(1 for t in dag.tasks.values() if t.status == TaskStatus.COMPLETED),
            "tasks_failed": sum(1 for t in dag.tasks.values() if t.status == TaskStatus.FAILED),
            "timestamp": end_time.isoformat()
        }
        
    def get_system_state(self) -> Dict:
        """Get comprehensive DAG system state."""
        total_workflows = len(self.workflows)
        
        # Calculate aggregate statistics
        total_tasks = sum(len(dag.tasks) for dag in self.workflows.values())
        avg_success_rate = sum(dag.success_rate for dag in self.workflows.values()) / total_workflows if total_workflows > 0 else 0
        avg_execution_time = sum(dag.avg_execution_time for dag in self.workflows.values()) / total_workflows if total_workflows > 0 else 0
        
        # Count workflows by status
        completed_workflows = sum(1 for dag in self.workflows.values() if dag.is_complete())
        failed_workflows = sum(1 for dag in self.workflows.values() if dag.has_failed())
        running_workflows = len(self.running_workflows)
        
        return {
            "total_workflows": total_workflows,
            "total_tasks": total_tasks,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "running_workflows": running_workflows,
            "avg_success_rate": avg_success_rate,
            "avg_execution_time": avg_execution_time,
            "workflows": {wid: workflow.to_dict() for wid, workflow in self.workflows.items()},
            "timestamp": datetime.now().isoformat()
        }


class PerformanceOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing DAG performance."""
    
    def get_name(self) -> str:
        return "dag_performance_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze DAG performance and identify optimization opportunities."""
        workflows_data = subsystem_state.get("workflows", {})
        opportunities = {
            "improvements_available": False,
            "slow_workflows": [],
            "bottleneck_tasks": [],
            "optimization_potential": 0.0
        }
        
        # Identify slow workflows (execution time > 2x average)
        avg_execution_time = subsystem_state.get("avg_execution_time", 300)
        for workflow_id, workflow_data in workflows_data.items():
            workflow_avg_time = workflow_data.get("avg_execution_time", 0)
            if workflow_avg_time > avg_execution_time * 1.5:
                opportunities["slow_workflows"].append({
                    "workflow_id": workflow_id,
                    "name": workflow_data.get("name", "Unknown"),
                    "avg_time": workflow_avg_time,
                    "slowdown_factor": workflow_avg_time / avg_execution_time
                })
                
        # Identify potential bottleneck tasks (long duration, many dependencies)
        for workflow_id, workflow_data in workflows_data.items():
            tasks = workflow_data.get("tasks", {})
            for task_id, task_data in tasks.items():
                estimated_duration = task_data.get("estimated_duration", 0)
                dependencies = len(task_data.get("dependencies", []))
                
                if estimated_duration > 120 and dependencies > 0:  # Long tasks with dependencies
                    opportunities["bottleneck_tasks"].append({
                        "workflow_id": workflow_id,
                        "task_id": task_id,
                        "task_name": task_data.get("name", "Unknown"),
                        "duration": estimated_duration,
                        "dependencies": dependencies
                    })
                    
        if opportunities["slow_workflows"] or opportunities["bottleneck_tasks"]:
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = (
                len(opportunities["slow_workflows"]) * 0.2 + 
                len(opportunities["bottleneck_tasks"]) * 0.1
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute DAG performance improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Optimize slow workflows
        for slow_workflow in opportunities.get("slow_workflows", []):
            workflow_id = slow_workflow["workflow_id"]
            if workflow_id in improved_state["workflows"]:
                # Simulate performance optimization by reducing execution time
                old_time = improved_state["workflows"][workflow_id]["avg_execution_time"]
                improvement_factor = 0.8  # 20% improvement
                improved_state["workflows"][workflow_id]["avg_execution_time"] = int(old_time * improvement_factor)
                
                improvements_made.append({
                    "type": "workflow_optimization",
                    "workflow_id": workflow_id,
                    "old_avg_time": old_time,
                    "new_avg_time": improved_state["workflows"][workflow_id]["avg_execution_time"]
                })
                
        # Optimize bottleneck tasks
        for bottleneck in opportunities.get("bottleneck_tasks", []):
            workflow_id = bottleneck["workflow_id"]
            task_id = bottleneck["task_id"]
            
            if (workflow_id in improved_state["workflows"] and 
                task_id in improved_state["workflows"][workflow_id]["tasks"]):
                
                # Simulate task optimization by reducing estimated duration
                old_duration = improved_state["workflows"][workflow_id]["tasks"][task_id]["estimated_duration"]
                improvement_factor = 0.75  # 25% improvement
                new_duration = int(old_duration * improvement_factor)
                improved_state["workflows"][workflow_id]["tasks"][task_id]["estimated_duration"] = new_duration
                
                improvements_made.append({
                    "type": "task_optimization",
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "old_duration": old_duration,
                    "new_duration": new_duration
                })
                
        # Recalculate system-wide averages
        if improvements_made:
            workflows = improved_state["workflows"].values()
            total_workflows = len(workflows)
            if total_workflows > 0:
                improved_state["avg_execution_time"] = sum(w["avg_execution_time"] for w in workflows) / total_workflows
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


class ReliabilityEnhancementStrategy(ImprovementStrategy):
    """Strategy for enhancing DAG reliability and error handling."""
    
    def get_name(self) -> str:
        return "dag_reliability_enhancement"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze DAG reliability and identify improvement opportunities."""
        workflows_data = subsystem_state.get("workflows", {})
        opportunities = {
            "improvements_available": False,
            "unreliable_workflows": [],
            "error_prone_tasks": [],
            "reliability_potential": 0.0
        }
        
        # Identify unreliable workflows (success rate < 90%)
        for workflow_id, workflow_data in workflows_data.items():
            success_rate = workflow_data.get("success_rate", 1.0)
            if success_rate < 0.9:
                opportunities["unreliable_workflows"].append({
                    "workflow_id": workflow_id,
                    "name": workflow_data.get("name", "Unknown"),
                    "success_rate": success_rate,
                    "reliability_gap": 0.95 - success_rate
                })
                
        if opportunities["unreliable_workflows"]:
            opportunities["improvements_available"] = True
            opportunities["reliability_potential"] = len(opportunities["unreliable_workflows"]) * 0.15
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute reliability improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Improve unreliable workflows
        for unreliable in opportunities.get("unreliable_workflows", []):
            workflow_id = unreliable["workflow_id"]
            if workflow_id in improved_state["workflows"]:
                # Simulate reliability improvement
                old_rate = improved_state["workflows"][workflow_id]["success_rate"]
                improvement = min(0.1, unreliable["reliability_gap"])
                new_rate = min(1.0, old_rate + improvement)
                improved_state["workflows"][workflow_id]["success_rate"] = new_rate
                
                improvements_made.append({
                    "type": "reliability_enhancement",
                    "workflow_id": workflow_id,
                    "old_success_rate": old_rate,
                    "new_success_rate": new_rate
                })
                
        # Recalculate system-wide average success rate
        if improvements_made:
            workflows = improved_state["workflows"].values()
            total_workflows = len(workflows)
            if total_workflows > 0:
                improved_state["avg_success_rate"] = sum(w["success_rate"] for w in workflows) / total_workflows
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


# Global DAG manager instance
_dag_manager = None


def get_dag_manager() -> DAGManager:
    """Get or create the global DAG manager."""
    global _dag_manager
    if _dag_manager is None:
        _dag_manager = DAGManager()
    return _dag_manager


def initialize_dag_management() -> SubsystemHook:
    """Initialize DAG management with recursive improvement hooks."""
    manager = get_dag_manager()
    
    # Create improvement strategies
    strategies = [
        PerformanceOptimizationStrategy(),
        ReliabilityEnhancementStrategy()
    ]
    
    # Create subsystem hook
    hook = SubsystemHook(
        name="dags",
        get_state_func=manager.get_system_state,
        improvement_strategies=strategies
    )
    
    # Register with the framework
    framework = get_framework()
    framework.register_subsystem(hook)
    
    return hook


# Example usage functions
def improve_dag_performance() -> Dict:
    """Manual trigger for DAG performance improvement."""
    framework = get_framework()
    return framework.run_manual_improvement("dags")


def get_dag_status() -> Dict:
    """Get current DAG system status."""
    manager = get_dag_manager()
    return manager.get_system_state()


if __name__ == "__main__":
    # Demo the DAG management system
    print("📊 EpochCore RAS DAG Management Demo")
    print("=" * 50)
    
    # Initialize
    hook = initialize_dag_management()
    manager = get_dag_manager()
    
    print("\n📈 Initial DAG Status:")
    status = get_dag_status()
    print(f"  Total Workflows: {status['total_workflows']}")
    print(f"  Total Tasks: {status['total_tasks']}")
    print(f"  Average Success Rate: {status['avg_success_rate']:.2%}")
    print(f"  Average Execution Time: {status['avg_execution_time']:.1f}s")
    
    print("\n🔧 Running Improvement Cycle...")
    improvement_result = improve_dag_performance()
    
    print(f"\n✅ Improvement Result: {improvement_result['status']}")
    if improvement_result['status'] == 'success':
        for improvement in improvement_result['improvements']:
            print(f"  Strategy: {improvement['strategy']}")
            if 'improvements_made' in improvement['after_state']:
                for imp in improvement['after_state']['improvements_made']:
                    print(f"    - {imp}")
    
    print("\n📈 Final DAG Status:")
    final_status = get_dag_status()
    print(f"  Total Workflows: {final_status['total_workflows']}")
    print(f"  Total Tasks: {final_status['total_tasks']}")
    print(f"  Average Success Rate: {final_status['avg_success_rate']:.2%}")
    print(f"  Average Execution Time: {final_status['avg_execution_time']:.1f}s")