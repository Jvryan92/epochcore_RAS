"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
Pattern definitions for the StrategyAgent's recursive task generation.
"""

from typing import List, Dict, Any
import uuid
from .strategy_agent import StrategyTask, TaskType, TaskPattern
from ..core.logger import get_logger

logger = get_logger(__name__)


def fractal_task_generator(task: StrategyTask, result: Any) -> List[StrategyTask]:
    """
    Generates tasks in a fractal pattern, where each task spawns smaller
    sub-patterns of itself with varying properties.
    """
    if task.depth >= task.metadata.get("max_depth", 4):
        return []

    scale_factor = task.metadata.get("scale_factor", 0.5)
    new_size = task.metadata.get("size", 1.0) * scale_factor
    rotation = task.metadata.get("rotation", 0) + 45

    subtasks = []
    for i in range(task.metadata.get("branches", 2)):
        new_task = StrategyTask(
            name=f"{task.name}_fractal_{task.depth}_{i}",
            description=f"Fractal subtask at depth {task.depth}",
            task_type=TaskType.RECURSIVE,
            metadata={
                "size": new_size,
                "rotation": rotation + (360 / task.metadata.get("branches", 2)) * i,
                "max_depth": task.metadata.get("max_depth", 4),
                "branches": task.metadata.get("branches", 2),
                "scale_factor": scale_factor,
            },
        )
        subtasks.append(new_task)

    return subtasks


def adaptive_split_generator(task: StrategyTask, result: Any) -> List[StrategyTask]:
    """
    Generates tasks that adapt based on the complexity and results of their parent task.
    """
    if not result or not isinstance(result, dict):
        return []

    complexity = result.get("complexity", 1)
    success_rate = result.get("success_rate", 1.0)

    # Adapt number of subtasks based on complexity and success
    num_subtasks = min(int(complexity * (2 - success_rate)), 5)

    subtasks = []
    for i in range(num_subtasks):
        new_task = StrategyTask(
            name=f"{task.name}_adaptive_{i}",
            description=f"Adaptive subtask {i} with complexity {complexity}",
            task_type=TaskType.META,
            metadata={
                "parent_complexity": complexity,
                "parent_success": success_rate,
                "adaptation_level": task.metadata.get("adaptation_level", 0) + 1,
            },
        )
        subtasks.append(new_task)

    return subtasks


def quantum_state_generator(task: StrategyTask, result: Any) -> List[StrategyTask]:
    """
    Generates tasks that exist in multiple states simultaneously until observed (executed).
    Support for bulk task generation through the bulk_factor metadata parameter.
    """
    states = ["analyze", "optimize", "transform", "validate"]
    if task.depth >= task.metadata.get("max_depth", 3):  # Configurable depth limit
        return []

    # Support for bulk generation
    bulk_factor = task.metadata.get("bulk_factor", 1)

    subtasks = []
    for state in states:
        probability = task.metadata.get(f"{state}_probability", 0.25)
        if probability > 0.1:  # Only create tasks with significant probability
            # Generate bulk_factor copies for each state
            for i in range(bulk_factor):
                new_task = StrategyTask(
                    name=f"{task.name}_{state}_{i+1}",
                    description=f"Quantum state task in {state} state",
                    task_type=TaskType.COMPOUND,
                    metadata={
                        "state": state,
                        "probability": probability,
                        "collapsed": False,
                        "superposition": states,
                        **{f"{s}_probability": probability * 0.5 for s in states},
                    },
                )
                subtasks.append(new_task)

    return subtasks


# Meta-handlers for processing specific task types
def complexity_analyzer(task: StrategyTask) -> Dict[str, Any]:
    """Analyzes and adjusts task complexity based on execution history."""
    history = task.metadata.get("execution_history", [])
    current_complexity = task.metadata.get("complexity", 1.0)

    if history:
        avg_success = sum(h.get("success_rate", 0) for h in history) / len(history)
        new_complexity = current_complexity * (1.5 - avg_success)
        task.metadata["complexity"] = new_complexity

    return {
        "analyzed_complexity": task.metadata.get("complexity", 1.0),
        "history_length": len(history),
        "recommended_subtasks": max(1, int(task.metadata.get("complexity", 1.0))),
    }


def pattern_optimizer(task: StrategyTask) -> List[StrategyTask]:
    """Optimizes task patterns based on previous execution results."""
    patterns = task.patterns
    optimized_tasks = []

    for pattern in patterns:
        if pattern.pattern_type == "fractal":
            # Optimize fractal parameters
            optimal_branches = task.metadata.get(
                "optimal_branches", task.metadata.get("branches", 2)
            )
            optimized_task = StrategyTask(
                name=f"{task.name}_optimized",
                task_type=TaskType.RECURSIVE,
                metadata={
                    "branches": optimal_branches,
                    "scale_factor": task.metadata.get("optimal_scale", 0.5),
                    "optimization_level": task.metadata.get("optimization_level", 0)
                    + 1,
                },
            )
            optimized_tasks.append(optimized_task)

    return optimized_tasks
