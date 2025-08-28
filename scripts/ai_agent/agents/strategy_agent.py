from ..core.base_agent import BaseAgent
from ..core.logger import get_logger
from typing import Dict, List, Any, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import uuid


class TaskType(Enum):
    """Types of tasks that can be processed by the agent."""

    STANDARD = "standard"
    META = "meta"  # Tasks that generate other tasks
    RECURSIVE = "recursive"  # Tasks that can spawn copies of themselves
    COMPOUND = "compound"  # Tasks with both meta and recursive properties


@dataclass
class TaskPattern:
    """Pattern for generating new tasks dynamically."""

    pattern_type: str
    generator: Callable[["StrategyTask", Any], List["StrategyTask"]]
    conditions: Dict[str, Any] = field(default_factory=dict)
    max_depth: int = 5
    max_branches: int = 3


@dataclass
class StrategyTask:
    """Represents a strategic task with potential subtasks and meta-capabilities."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.STANDARD
    subtasks: List["StrategyTask"] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    patterns: List[TaskPattern] = field(default_factory=list)
    status: str = "pending"
    depth: int = 0
    result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    visited_states: Set[str] = field(default_factory=set)


class StrategyAgent(BaseAgent):
    """
    Dedicated AI agent for automating strategic tasks in StrategyDECK.
    Features double recursion through meta-task processing and dynamic task generation.
    """

    def __init__(self, name="strategy_agent", config=None):
        super().__init__(name, config)
        self.logger = get_logger(name)
        self.task_graph = defaultdict(list)
        self.tasks = {}
        self.results_cache = {}
        self.pattern_registry = {}
        self.meta_handlers = defaultdict(list)
        self.state_history = defaultdict(list)
        self.execution_depth = 0
        self.max_recursion_depth = 10  # Configurable

        # Initialize with default patterns
        from .patterns import (
            fractal_task_generator,
            adaptive_split_generator,
            quantum_state_generator,
            complexity_analyzer,
            pattern_optimizer,
        )

        # Register default patterns
        self.register_pattern(
            "fractal",
            TaskPattern(
                pattern_type="fractal",
                generator=fractal_task_generator,
                max_depth=4,
                max_branches=4,
            ),
        )

        self.register_pattern(
            "adaptive",
            TaskPattern(
                pattern_type="adaptive",
                generator=adaptive_split_generator,
                max_depth=5,
                max_branches=5,
            ),
        )

        self.register_pattern(
            "quantum",
            TaskPattern(
                pattern_type="quantum",
                generator=quantum_state_generator,
                max_depth=3,
                max_branches=4,
            ),
        )

        # Register meta-handlers
        self.register_meta_handler(TaskType.META.value, complexity_analyzer)
        self.register_meta_handler(TaskType.COMPOUND.value, pattern_optimizer)

    def validate_config(self) -> bool:
        """Validate the agent's configuration."""
        # Basic config validation
        if (
            not isinstance(self.max_recursion_depth, int)
            or self.max_recursion_depth < 1
        ):
            return False

        # Ensure we have at least one pattern registered
        if not self.pattern_registry:
            return False

        return True

    def add_task(self, task: StrategyTask) -> None:
        """Add a task to the agent's task graph."""
        self.tasks[task.id] = task
        if task.dependencies:
            for dep in task.dependencies:
                self.task_graph[dep].append(task.id)

    def create_bulk_task(
        self, name: str, bulk_factor: int = 100, pattern_type: str = "quantum"
    ) -> StrategyTask:
        """
        Create a task that will generate bulk_factor outputs.

        Args:
            name: Base name for the task
            bulk_factor: Number of outputs to generate (default 100)
            pattern_type: Type of pattern to use ('quantum', 'fractal', 'adaptive')

        Returns:
            StrategyTask: The created bulk task
        """
        task = StrategyTask(
            name=f"{name}_bulk_{bulk_factor}x",
            description=f"Bulk task generator for {bulk_factor} outputs",
            task_type=TaskType.COMPOUND,
            metadata={
                "bulk_factor": bulk_factor,
                "max_depth": 5,  # Allow deeper recursion for bulk tasks
                "optimization_level": 2,
                "analyze_probability": 0.25,
                "optimize_probability": 0.25,
                "transform_probability": 0.25,
                "validate_probability": 0.25,
            },
        )

        # Add the specified pattern
        if pattern_type in self.pattern_registry:
            pattern = self.pattern_registry[pattern_type]
            task.patterns.append(pattern)

        self.add_task(task)
        return task

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the current status of a task."""
        return self.tasks[task_id].status if task_id in self.tasks else None

    def register_pattern(self, name: str, pattern: TaskPattern) -> None:
        """Register a new task generation pattern."""
        self.pattern_registry[name] = pattern

    def register_meta_handler(self, task_type: str, handler: Callable) -> None:
        """Register a handler for meta-task processing."""
        self.meta_handlers[task_type].append(handler)

    def _generate_dynamic_tasks(self, task: StrategyTask) -> List[StrategyTask]:
        """Generate new tasks based on patterns and current state."""
        new_tasks = []

        # Skip if we've reached maximum depth
        if task.depth >= self.max_recursion_depth:
            self.logger.warning(f"Max recursion depth reached for task {task.id}")
            return new_tasks

        # Apply each pattern registered for the task
        for pattern in task.patterns:
            if pattern.max_depth > task.depth:
                # Check if we've seen this state before to prevent infinite loops
                state_key = f"{task.id}:{pattern.pattern_type}"
                if state_key not in task.visited_states:
                    task.visited_states.add(state_key)

                    # Generate new tasks using the pattern
                    generated = pattern.generator(task, task.result)
                    for new_task in generated:
                        new_task.depth = task.depth + 1
                        new_tasks.append(new_task)

        return new_tasks

    def execute_task(self, task: StrategyTask) -> Any:
        """Execute a single task with double recursion capabilities."""
        if task.id in self.results_cache:
            return self.results_cache[task.id]

        self.execution_depth += 1
        try:
            # Process dependencies first
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks:
                        raise ValueError(f"Dependency {dep_id} not found")
                    if self.tasks[dep_id].status != "completed":
                        self.execute_task(self.tasks[dep_id])

            # First level of recursion: process subtasks
            subtask_results = []
            if task.subtasks:
                for subtask in task.subtasks:
                    subtask_result = self.execute_task(subtask)
                    subtask_results.append(subtask_result)
                task.result = subtask_results
            else:
                # Process the task itself
                task.result = self._process_task(task)

            # Second level of recursion: handle meta-tasks and dynamic generation
            if task.task_type in (TaskType.META, TaskType.COMPOUND):
                # Execute meta-handlers
                for handler in self.meta_handlers[task.task_type.value]:
                    handler(task)

            # Generate and process dynamic tasks
            task.result = task.result or []  # Initialize result list if needed
            if not isinstance(task.result, list):
                task.result = [task.result]

            new_tasks = self._generate_dynamic_tasks(task)
            if new_tasks:
                # Store generated tasks for meta result
                task.metadata["generated_tasks"] = new_tasks
                # Add new tasks to the system and execute them
                for new_task in new_tasks:
                    self.add_task(new_task)
                    new_result = self.execute_task(new_task)
                    task.result.append(new_result)

            # Set proper status based on task type
            task.status = (
                "compound_processed"
                if task.task_type == TaskType.COMPOUND
                else "completed"
            )
            # Wrap results in proper response format
            results = {
                "status": task.status,
                "task_id": task.id,
                "result": task.result,
                "meta_result": self._process_meta_task(task),
                "recursive_result": self._process_recursive_task(task),
            }
            self.results_cache[task.id] = results
            return results

        finally:
            self.execution_depth -= 1

    def _process_task(self, task: StrategyTask) -> Any:
        """Process a task with state tracking and advanced pattern matching."""
        self.logger.info(
            f"Processing task: {task.name} (Type: {task.task_type.value}, Depth: {task.depth})"
        )

        # Track task state
        state_snapshot = {
            "type": task.task_type.value,
            "depth": task.depth,
            "dependencies_completed": all(
                self.tasks[dep].status == "completed" for dep in task.dependencies
            ),
            "patterns_available": len(task.patterns),
            "metadata": task.metadata.copy(),
        }
        self.state_history[task.id].append(state_snapshot)

        # Apply type-specific processing
        if task.task_type == TaskType.RECURSIVE:
            return self._process_recursive_task(task)
        elif task.task_type == TaskType.META:
            return self._process_meta_task(task)
        elif task.task_type == TaskType.COMPOUND:
            return self._process_compound_task(task)
        else:
            return {"status": "processed", "task_id": task.id, "state": state_snapshot}

    def _process_recursive_task(self, task: StrategyTask) -> Any:
        """Handle tasks that can spawn copies of themselves."""
        if task.depth >= self.max_recursion_depth:
            return {"status": "max_depth_reached", "task_id": task.id}

        # Create a recursive copy if conditions are met
        state_key = f"recursive:{task.id}:{task.depth}"
        if state_key not in task.visited_states:
            task.visited_states.add(state_key)

            new_task = StrategyTask(
                name=f"{task.name}_recursive_{task.depth + 1}",
                description=f"Recursive instance of {task.name}",
                task_type=TaskType.RECURSIVE,
                depth=task.depth + 1,
                patterns=task.patterns,
                metadata=task.metadata.copy(),
            )
            return {"status": "spawned", "task_id": task.id, "new_task": new_task}

        return {"status": "terminal", "task_id": task.id}

    def _process_meta_task(self, task: StrategyTask) -> Any:
        """Handle tasks that generate other tasks."""
        generated_tasks = task.metadata.get("generated_tasks", [])

        # Apply each registered meta-handler
        for handler in self.meta_handlers[task.task_type.value]:
            result = handler(task)
            if isinstance(result, list):
                generated_tasks.extend(result)

        return {
            "status": "meta_processed",
            "task_id": task.id,
            "generated_tasks": len(generated_tasks),
            "tasks": generated_tasks,
        }

    def _process_compound_task(self, task: StrategyTask) -> Any:
        """Handle tasks with both meta and recursive properties."""
        # First handle meta-task generation
        meta_result = self._process_meta_task(task)

        # Then handle recursive processing
        recursive_result = self._process_recursive_task(task)

        return {
            "status": "compound_processed",
            "task_id": task.id,
            "meta_result": meta_result,
            "recursive_result": recursive_result,
        }

    def run(self, *args, **kwargs):
        """
        Main entry point for agent execution with double recursion capabilities.
        """
        try:
            self.logger.info(f"{self.name} started with double recursion enabled.")
            self.execution_depth = 0

            # Find root tasks (those with no dependencies)
            root_tasks = [task for task in self.tasks.values() if not task.dependencies]

            # Execute all root tasks with state tracking
            results = []
            for task in root_tasks:
                result = self.execute_task(task)
                results.append(
                    {
                        "task_id": task.id,
                        "result": result,
                        "state_history": self.state_history[task.id],
                        "final_depth": task.depth,
                    }
                )

            self.logger.info(
                f"{self.name} completed successfully. Max depth reached: {max(task.depth for task in self.tasks.values())}"
            )
            return {
                "status": "success",
                "results": results,
                "max_depth": max(task.depth for task in self.tasks.values()),
            }

        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}")
            raise
        finally:
            # Clear execution state
            self.execution_depth = 0
